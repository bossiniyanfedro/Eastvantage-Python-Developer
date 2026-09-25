import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.distance import haversine
from app.main import app

class AddressApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.test_engine
        )
        Base.metadata.create_all(bind=cls.test_engine)

        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    def test_haversine_distance(self):
        d = haversine(-6.175392, 106.827153, -6.1950, 106.8230)
        self.assertAlmostEqual(d, 2.23, delta=0.2)
        self.assertEqual(haversine(14.55, 121.02, 14.55, 121.02), 0.0)

    def test_create_and_read_address(self):
        payload = {
            "name": "Eastvantage Office",
            "street": "123 Ayala Ave",
            "city": "Makati",
            "country": "Philippines",
            "latitude": 14.5547,
            "longitude": 121.0244,
        }
        res = self.client.post("/addresses", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "Eastvantage Office")
        self.assertEqual(data["latitude"], 14.5547)

        addr_id = data["id"]
        res_get = self.client.get(f"/addresses/{addr_id}")
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.json()["city"], "Makati")

    def test_create_address_validation(self):
        bad_lat = {
            "name": "Bad Lat",
            "street": "Some Street",
            "city": "City",
            "country": "Country",
            "latitude": 95.0,
            "longitude": 120.0,
        }
        res = self.client.post("/addresses", json=bad_lat)
        self.assertEqual(res.status_code, 422)

        bad_lon = {
            "name": "Bad Lon",
            "street": "Some Street",
            "city": "City",
            "country": "Country",
            "latitude": 14.0,
            "longitude": 185.0,
        }
        res = self.client.post("/addresses", json=bad_lon)
        self.assertEqual(res.status_code, 422)

        blank_name = {
            "name": "   ",
            "street": "Some Street",
            "city": "City",
            "country": "Country",
            "latitude": 14.0,
            "longitude": 120.0,
        }
        res = self.client.post("/addresses", json=blank_name)
        self.assertEqual(res.status_code, 422)

    def test_update_address(self):
        created = self.client.post(
            "/addresses",
            json={
                "name": "Original Name",
                "street": "Street 1",
                "city": "City 1",
                "country": "Country 1",
                "latitude": 10.0,
                "longitude": 20.0,
            },
        ).json()
        addr_id = created["id"]

        res = self.client.put(f"/addresses/{addr_id}", json={"name": "Updated Name"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["name"], "Updated Name")
        self.assertEqual(res.json()["city"], "City 1")

        res_empty = self.client.put(f"/addresses/{addr_id}", json={})
        self.assertEqual(res_empty.status_code, 400)

        res_404 = self.client.put("/addresses/99999", json={"name": "Nobody"})
        self.assertEqual(res_404.status_code, 404)

    def test_delete_address(self):
        created = self.client.post(
            "/addresses",
            json={
                "name": "To Delete",
                "street": "Delete St",
                "city": "Delete City",
                "country": "Country",
                "latitude": 1.0,
                "longitude": 1.0,
            },
        ).json()
        addr_id = created["id"]

        res = self.client.delete(f"/addresses/{addr_id}")
        self.assertEqual(res.status_code, 200)

        res_check = self.client.get(f"/addresses/{addr_id}")
        self.assertEqual(res_check.status_code, 404)

        res_again = self.client.delete(f"/addresses/{addr_id}")
        self.assertEqual(res_again.status_code, 404)

    def test_nearby_search(self):
        self.client.post(
            "/addresses",
            json={
                "name": "Makati Hub",
                "street": "Ayala Ave",
                "city": "Makati",
                "country": "Philippines",
                "latitude": 14.5547,
                "longitude": 121.0244,
            },
        )
        self.client.post(
            "/addresses",
            json={
                "name": "QC Branch",
                "street": "EDSA",
                "city": "Quezon City",
                "country": "Philippines",
                "latitude": 14.6500,
                "longitude": 121.0300,
            },
        )

        res_5km = self.client.get(
            "/addresses/nearby",
            params={"latitude": 14.5547, "longitude": 121.0244, "distance_km": 5},
        )
        self.assertEqual(res_5km.status_code, 200)
        items_5km = res_5km.json()
        names_5km = [item["name"] for item in items_5km]
        self.assertIn("Makati Hub", names_5km)
        self.assertNotIn("QC Branch", names_5km)

        res_20km = self.client.get(
            "/addresses/nearby",
            params={"latitude": 14.5547, "longitude": 121.0244, "distance_km": 20},
        )
        self.assertEqual(res_20km.status_code, 200)
        items_20km = res_20km.json()
        names_20km = [item["name"] for item in items_20km]
        self.assertIn("Makati Hub", names_20km)
        self.assertIn("QC Branch", names_20km)

        distances = [item["distance_km"] for item in items_20km]
        self.assertEqual(distances, sorted(distances))


if __name__ == "__main__":
    unittest.main()
