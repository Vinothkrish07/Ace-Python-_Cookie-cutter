"""Basic unit tests for global_ui_settings API router using shared test_client fixture."""


def test_read_global_ui_settings_success(test_client) -> None:
    """Test successful retrieval of global UI settings."""
    r = test_client.get("/api/v1/global_ui_settings/")

    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "settings" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert isinstance(data["settings"], dict)


def test_read_global_ui_settings_non_staff_denied(test_client_non_staff) -> None:
    """Test that non-staff users are denied access to global UI settings."""
    r = test_client_non_staff.get("/api/v1/global_ui_settings/")

    assert r.status_code == 403
    assert r.json()["detail"] == "Not enough permissions"


def test_update_global_ui_settings_success(test_client) -> None:
    """Test successful update of global UI settings."""
    payload = {"theme": "dark", "language": "en", "notifications": True}
    r = test_client.post("/api/v1/global_ui_settings/", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "settings" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["settings"] == payload


def test_update_global_ui_settings_non_staff_denied(test_client_non_staff) -> None:
    """Test that non-staff users are denied access to update global UI settings."""
    payload = {"theme": "dark", "language": "en"}
    r = test_client_non_staff.post("/api/v1/global_ui_settings/", json=payload)

    assert r.status_code == 403
    assert r.json()["detail"] == "Not enough permissions"


def test_update_global_ui_settings_empty_payload(test_client) -> None:
    """Test update with empty settings payload."""
    payload = {}
    r = test_client.post("/api/v1/global_ui_settings/", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert data["settings"] == payload


def test_read_global_ui_settings_syncs_success(test_client) -> None:
    """Test successful retrieval of global UI settings syncs."""
    r = test_client.get("/api/v1/global_ui_settings/syncs")

    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_read_global_ui_settings_syncs_with_pagination(test_client) -> None:
    """Test retrieval of global UI settings syncs with pagination parameters."""
    r = test_client.get("/api/v1/global_ui_settings/syncs?skip=0&limit=50")

    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_read_global_ui_settings_syncs_non_staff_denied(test_client_non_staff) -> None:
    """Test that non-staff users are denied access to global UI settings syncs."""
    r = test_client_non_staff.get("/api/v1/global_ui_settings/syncs")

    assert r.status_code == 403
    assert r.json()["detail"] == "Not enough permissions"


def test_create_global_ui_settings_sync_success(test_client) -> None:
    """Test successful creation of global UI settings sync."""
    r = test_client.post("/api/v1/global_ui_settings/syncs")

    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "type" in data
    assert "status" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["type"] == "global_ui_settings"
    assert data["status"] == "pending"


def test_create_global_ui_settings_sync_non_staff_denied(test_client_non_staff) -> None:
    """Test that non-staff users are denied access to create global UI settings sync."""
    r = test_client_non_staff.post("/api/v1/global_ui_settings/syncs")

    assert r.status_code == 403
    assert r.json()["detail"] == "Not enough permissions"


def test_read_global_ui_settings_sync_by_id_success(test_client) -> None:
    """Test successful retrieval of specific global UI settings sync."""
    sync_id = 123
    r = test_client.get(f"/api/v1/global_ui_settings/syncs/{sync_id}")

    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "type" in data
    assert "status" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["id"] == sync_id
    assert data["type"] == "global_ui_settings"


def test_read_global_ui_settings_sync_by_id_non_staff_denied(test_client_non_staff) -> None:
    """Test that non-staff users are denied access to specific global UI settings sync."""
    sync_id = 123
    r = test_client_non_staff.get(f"/api/v1/global_ui_settings/syncs/{sync_id}")

    assert r.status_code == 403
    assert r.json()["detail"] == "Not enough permissions"


def test_new_global_ui_settings_sync_success(test_client) -> None:
    """Test successful retrieval of form data for new global UI settings sync."""
    r = test_client.get("/api/v1/global_ui_settings/syncs/new")

    assert r.status_code == 200
    data = r.json()
    assert "sync_types" in data
    assert "default_sync" in data
    assert isinstance(data["sync_types"], list)
    assert isinstance(data["default_sync"], dict)
    assert "full" in data["sync_types"]
    assert "partial" in data["sync_types"]
    assert "incremental" in data["sync_types"]


def test_new_global_ui_settings_sync_non_staff_denied(test_client_non_staff) -> None:
    """Test that non-staff users are denied access to new global UI settings sync form."""
    r = test_client_non_staff.get("/api/v1/global_ui_settings/syncs/new")

    assert r.status_code == 403
    assert r.json()["detail"] == "Not enough permissions"


def test_read_global_ui_user_settings_success(test_client) -> None:
    """Test successful retrieval of global UI user settings."""
    r = test_client.get("/api/v1/global_ui_settings/user_settings")

    assert r.status_code == 200
    data = r.json()
    assert "theme" in data
    assert "language" in data
    assert data["theme"] == "light"
    assert data["language"] == "en"


def test_read_global_ui_user_settings_non_staff_success(test_client_non_staff) -> None:
    """Test that non-staff users can access their own user settings."""
    r = test_client_non_staff.get("/api/v1/global_ui_settings/user_settings")

    assert r.status_code == 200
    data = r.json()
    assert "theme" in data
    assert "language" in data
    assert data["theme"] == "light"
    assert data["language"] == "en"


def test_update_global_ui_user_settings_success(test_client) -> None:
    """Test successful update of global UI user settings."""
    payload = {"theme": "dark", "language": "es", "notifications": False}
    r = test_client.post("/api/v1/global_ui_settings/user_settings", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert data == payload


def test_update_global_ui_user_settings_non_staff_success(test_client_non_staff) -> None:
    """Test that non-staff users can update their own user settings."""
    payload = {"theme": "dark", "language": "fr"}
    r = test_client_non_staff.post("/api/v1/global_ui_settings/user_settings", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert data == payload


def test_update_global_ui_user_settings_empty_payload(test_client) -> None:
    """Test update with empty user settings payload."""
    payload = {}
    r = test_client.post("/api/v1/global_ui_settings/user_settings", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert data == payload


def test_read_global_ui_user_settings_syncs_success(test_client) -> None:
    """Test successful retrieval of global UI user settings syncs."""
    r = test_client.get("/api/v1/global_ui_settings/user_settings/syncs")

    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_read_global_ui_user_settings_syncs_with_pagination(test_client) -> None:
    """Test retrieval of global UI user settings syncs with pagination parameters."""
    r = test_client.get("/api/v1/global_ui_settings/user_settings/syncs?skip=10&limit=25")

    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_read_global_ui_user_settings_syncs_non_staff_success(test_client_non_staff) -> None:
    """Test that non-staff users can access their own user settings syncs."""
    r = test_client_non_staff.get("/api/v1/global_ui_settings/user_settings/syncs")

    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_create_global_ui_user_settings_sync_success(test_client) -> None:
    """Test successful creation of global UI user settings sync."""
    r = test_client.post("/api/v1/global_ui_settings/user_settings/syncs")

    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "type" in data
    assert "status" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["type"] == "global_ui_user_settings"
    assert data["status"] == "pending"


def test_create_global_ui_user_settings_sync_non_staff_success(test_client_non_staff) -> None:
    """Test that non-staff users can create their own user settings sync."""
    r = test_client_non_staff.post("/api/v1/global_ui_settings/user_settings/syncs")

    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert "type" in data
    assert "status" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["type"] == "global_ui_user_settings"
    assert data["status"] == "pending"


def test_invalid_json_payload(test_client) -> None:
    """Test handling of invalid JSON payload."""
    r = test_client.post(
        "/api/v1/global_ui_settings/",
        data="invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert r.status_code == 422


def test_invalid_user_settings_json_payload(test_client) -> None:
    """Test handling of invalid JSON payload for user settings."""
    r = test_client.post(
        "/api/v1/global_ui_settings/user_settings",
        data="invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert r.status_code == 422


def test_sync_id_parameter_types(test_client) -> None:
    """Test that sync ID parameter accepts different integer values."""
    # Test with different integer values
    for sync_id in [1, 999, 0, -1]:
        r = test_client.get(f"/api/v1/global_ui_settings/syncs/{sync_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == sync_id


def test_pagination_parameters_edge_cases(test_client) -> None:
    """Test pagination parameters with edge case values."""
    # Test with zero values
    r = test_client.get("/api/v1/global_ui_settings/syncs?skip=0&limit=0")
    assert r.status_code == 200

    # Test with large values
    r = test_client.get("/api/v1/global_ui_settings/syncs?skip=1000&limit=1000")
    assert r.status_code == 200


def test_user_settings_pagination_parameters_edge_cases(test_client) -> None:
    """Test user settings pagination parameters with edge case values."""
    # Test with zero values
    r = test_client.get("/api/v1/global_ui_settings/user_settings/syncs?skip=0&limit=0")
    assert r.status_code == 200

    # Test with large values
    r = test_client.get("/api/v1/global_ui_settings/user_settings/syncs?skip=1000&limit=1000")
    assert r.status_code == 200


def test_complex_settings_payload(test_client) -> None:
    """Test update with complex nested settings payload."""
    payload = {
        "theme": "dark",
        "language": "en",
        "notifications": {
            "email": True,
            "push": False,
            "sms": True,
        },
        "layout": {
            "sidebar": "collapsed",
            "header": "fixed",
        },
        "features": ["feature1", "feature2", "feature3"],
        "metadata": {
            "version": "1.0",
            "last_updated": "2024-01-01T00:00:00Z",
        },
    }
    r = test_client.post("/api/v1/global_ui_settings/", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert data["settings"] == payload


def test_complex_user_settings_payload(test_client) -> None:
    """Test update with complex nested user settings payload."""
    payload = {
        "preferences": {
            "theme": "auto",
            "language": "en",
            "timezone": "UTC",
        },
        "dashboard": {
            "widgets": ["widget1", "widget2"],
            "layout": "grid",
        },
        "accessibility": {
            "high_contrast": False,
            "font_size": "medium",
        },
    }
    r = test_client.post("/api/v1/global_ui_settings/user_settings", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert data == payload
