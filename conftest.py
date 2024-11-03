def pytest_sessionstart(session):
    from main import generate_data
    generate_data()