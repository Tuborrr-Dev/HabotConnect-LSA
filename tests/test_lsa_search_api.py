"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

import json
from sqlalchemy import event
from sqlalchemy.engine import Engine
from tests.base import BaseTestCase
from app.extensions import db


class TestLSASearchAPI(BaseTestCase):
    def test_tc09_no_filters(self):
        lsa1 = self.create_lsa(full_name="LSA 1", email="lsa1@test.com")
        lsa2 = self.create_lsa(full_name="LSA 2", email="lsa2@test.com")
        lsa3 = self.create_lsa(full_name="LSA 3", email="lsa3@test.com")
        skill = self.create_skill("Dyslexia Support")
        lsa1.skills.append(skill)
        db.session.commit()

        response = self.client.get("/api/v1/lsas/search/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data["results"]), 3)
        self.assertEqual(data["total_results"], 3)
        self.assertIn("skills", data["results"][0])

    def test_tc10_filter_by_skill(self):
        lsa1 = self.create_lsa(full_name="LSA 1", email="lsa1@test.com")
        lsa2 = self.create_lsa(full_name="LSA 2", email="lsa2@test.com")
        skill1 = self.create_skill("ADHD Coaching")
        skill2 = self.create_skill("Autism Support")
        lsa1.skills.append(skill1)
        lsa2.skills.append(skill2)
        db.session.commit()

        response = self.client.get("/api/v1/lsas/search/?skills=ADHD Coaching")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["full_name"], "LSA 1")

    def test_tc11_filter_nonexistent_skill(self):
        lsa = self.create_lsa()
        skill = self.create_skill("Real Skill")
        lsa.skills.append(skill)
        db.session.commit()

        response = self.client.get("/api/v1/lsas/search/?skills=Nonexistent Skill")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["results"], [])
        self.assertEqual(data["total_results"], 0)

    def test_tc12_page_size_above_max(self):
        response = self.client.get("/api/v1/lsas/search/?page_size=500")
        self.assertEqual(response.status_code, 400)

    def test_tc13_n_plus_one_guard(self):
        skills = [self.create_skill(f"Skill {i}") for i in range(50)]
        for i in range(25):
            lsa = self.create_lsa(full_name=f"LSA {i}", email=f"lsa{i}@test.com")
            lsa.skills.append(skills[i * 2])
            lsa.skills.append(skills[i * 2 + 1])
        db.session.commit()

        query_count = [0]

        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            query_count[0] += 1

        event.listen(Engine, "before_cursor_execute", before_cursor_execute)
        try:
            response = self.client.get("/api/v1/lsas/search/?page_size=25")
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data["results"]), 25)
            # count() + main select + selectinload skills = 3 queries
            self.assertEqual(query_count[0], 3)
        finally:
            event.remove(Engine, "before_cursor_execute", before_cursor_execute)
