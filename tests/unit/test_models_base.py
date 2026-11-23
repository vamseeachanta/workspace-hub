"""
ABOUTME: Unit tests for BaseModel and ORM mixins
ABOUTME: Tests model instantiation, field defaults, timestamps, and mixin functionality
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker

from src.models.base import (
    Base, BaseModel, AuditMixin, MetadataMixin, StatusMixin
)


# Test model classes
class TestModel(BaseModel):
    """Test model extending BaseModel."""
    __tablename__ = 'test_models'
    name = Column(String(255), nullable=False)


class AuditedModel(BaseModel, AuditMixin):
    """Test model with audit tracking."""
    __tablename__ = 'audited_models'
    name = Column(String(255), nullable=False)


class MetadataModel(BaseModel, MetadataMixin):
    """Test model with metadata support."""
    __tablename__ = 'metadata_models'
    name = Column(String(255), nullable=False)


class StatusModel(BaseModel, StatusMixin):
    """Test model with status tracking."""
    __tablename__ = 'status_models'
    name = Column(String(255), nullable=False)


class FullModel(BaseModel, AuditMixin, MetadataMixin, StatusMixin):
    """Test model with all mixins."""
    __tablename__ = 'full_models'
    name = Column(String(255), nullable=False)


class TestBaseModel:
    """Test BaseModel functionality."""

    @pytest.fixture
    def db_session(self):
        """Create in-memory SQLite database for testing."""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_model_instantiation(self, db_session):
        """Test creating a model instance."""
        model = TestModel(name='test_instance')

        assert model.name == 'test_instance'
        assert model.is_active is True

    def test_base_fields_default_values(self, db_session):
        """Test that base fields have correct defaults."""
        model = TestModel(name='test')

        assert model.id is None  # Not yet committed
        assert model.created_at is None  # Set on commit
        assert model.updated_at is None  # Set on commit
        assert model.is_active is True

    def test_timestamps_on_commit(self, db_session):
        """Test that timestamps are set on commit."""
        model = TestModel(name='test')
        db_session.add(model)
        db_session.commit()

        assert model.id is not None
        assert model.created_at is not None
        assert model.updated_at is not None
        assert isinstance(model.created_at, datetime)

    def test_model_to_dict(self, db_session):
        """Test converting model to dictionary."""
        model = TestModel(name='test')
        db_session.add(model)
        db_session.commit()

        model_dict = model.to_dict()

        assert 'id' in model_dict
        assert 'created_at' in model_dict
        assert 'updated_at' in model_dict
        assert 'is_active' in model_dict
        assert model_dict['is_active'] is True

    def test_model_repr(self, db_session):
        """Test model string representation."""
        model = TestModel(name='test')
        db_session.add(model)
        db_session.commit()

        repr_str = repr(model)
        assert 'TestModel' in repr_str
        assert f'id={model.id}' in repr_str

    def test_is_active_field(self, db_session):
        """Test is_active field functionality."""
        model = TestModel(name='test')
        db_session.add(model)
        db_session.commit()

        assert model.is_active is True

        # Test soft delete concept
        model.is_active = False
        db_session.commit()

        retrieved = db_session.query(TestModel).filter_by(id=model.id).first()
        assert retrieved.is_active is False

    def test_multiple_instances(self, db_session):
        """Test creating multiple model instances."""
        model1 = TestModel(name='instance1')
        model2 = TestModel(name='instance2')

        db_session.add_all([model1, model2])
        db_session.commit()

        assert model1.id != model2.id
        assert model1.created_at is not None
        assert model2.created_at is not None


class TestAuditMixin:
    """Test AuditMixin functionality."""

    @pytest.fixture
    def db_session(self):
        """Create in-memory SQLite database."""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_audit_fields_exist(self, db_session):
        """Test that audit fields are present."""
        model = AuditedModel(name='test')

        assert hasattr(model, 'created_by')
        assert hasattr(model, 'updated_by')
        assert hasattr(model, 'change_notes')

    def test_audit_defaults(self, db_session):
        """Test audit field defaults."""
        model = AuditedModel(name='test')
        db_session.add(model)
        db_session.commit()

        assert model.created_by is None
        assert model.updated_by is None
        assert model.change_notes is None

    def test_audit_tracking(self, db_session):
        """Test setting audit values."""
        model = AuditedModel(name='test', created_by='admin')
        db_session.add(model)
        db_session.commit()

        model.updated_by = 'admin2'
        model.change_notes = 'Updated field name'
        db_session.commit()

        retrieved = db_session.query(AuditedModel).filter_by(id=model.id).first()
        assert retrieved.created_by == 'admin'
        assert retrieved.updated_by == 'admin2'
        assert retrieved.change_notes == 'Updated field name'


class TestMetadataMixin:
    """Test MetadataMixin functionality."""

    @pytest.fixture
    def db_session(self):
        """Create in-memory SQLite database."""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_metadata_fields_exist(self, db_session):
        """Test that metadata fields exist."""
        model = MetadataModel(name='test')

        assert hasattr(model, 'metadata_json')
        assert hasattr(model, 'tags')
        assert hasattr(model, 'version')

    def test_version_default(self, db_session):
        """Test that version defaults to 1."""
        model = MetadataModel(name='test')
        db_session.add(model)
        db_session.commit()

        assert model.version == 1

    def test_metadata_json_storage(self, db_session):
        """Test storing JSON metadata."""
        metadata = {'key': 'value', 'nested': {'data': 123}}
        model = MetadataModel(name='test', metadata_json=metadata)

        db_session.add(model)
        db_session.commit()

        retrieved = db_session.query(MetadataModel).filter_by(id=model.id).first()
        assert retrieved.metadata_json == metadata

    def test_tags_storage(self, db_session):
        """Test storing tags as JSON array."""
        tags = ['tag1', 'tag2', 'tag3']
        model = MetadataModel(name='test', tags=tags)

        db_session.add(model)
        db_session.commit()

        retrieved = db_session.query(MetadataModel).filter_by(id=model.id).first()
        assert retrieved.tags == tags

    def test_version_increment(self, db_session):
        """Test incrementing version on update."""
        model = MetadataModel(name='test')
        db_session.add(model)
        db_session.commit()

        original_version = model.version

        # Increment version
        model.version = 2
        db_session.commit()

        retrieved = db_session.query(MetadataModel).filter_by(id=model.id).first()
        assert retrieved.version == 2


class TestStatusMixin:
    """Test StatusMixin functionality."""

    @pytest.fixture
    def db_session(self):
        """Create in-memory SQLite database."""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_status_fields_exist(self, db_session):
        """Test that status fields exist."""
        model = StatusModel(name='test')

        assert hasattr(model, 'status')
        assert hasattr(model, 'status_message')
        assert hasattr(model, 'status_updated_at')

    def test_status_default(self, db_session):
        """Test that status defaults to 'pending'."""
        model = StatusModel(name='test')
        db_session.add(model)
        db_session.commit()

        assert model.status == 'pending'

    def test_status_transition(self, db_session):
        """Test changing status."""
        model = StatusModel(name='test', status='pending')
        db_session.add(model)
        db_session.commit()

        model.status = 'processing'
        model.status_message = 'Currently processing'
        db_session.commit()

        retrieved = db_session.query(StatusModel).filter_by(id=model.id).first()
        assert retrieved.status == 'processing'
        assert retrieved.status_message == 'Currently processing'

    def test_status_updated_at_timestamp(self, db_session):
        """Test that status_updated_at is set."""
        model = StatusModel(name='test')
        db_session.add(model)
        db_session.commit()

        assert model.status_updated_at is not None
        assert isinstance(model.status_updated_at, datetime)

    def test_valid_status_values(self, db_session):
        """Test various status values."""
        statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']

        for status in statuses:
            model = StatusModel(name=f'test_{status}', status=status)
            db_session.add(model)

        db_session.commit()

        for i, status in enumerate(statuses):
            retrieved = db_session.query(StatusModel).filter_by(status=status).first()
            assert retrieved.status == status


class TestFullModel:
    """Test model with all mixins combined."""

    @pytest.fixture
    def db_session(self):
        """Create in-memory SQLite database."""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_full_model_all_fields(self, db_session):
        """Test that full model has all fields from all mixins."""
        model = FullModel(
            name='full_test',
            created_by='admin',
            metadata_json={'data': 'value'},
            status='processing'
        )

        db_session.add(model)
        db_session.commit()

        # Verify base fields
        assert model.id is not None
        assert model.is_active is True

        # Verify audit fields
        assert model.created_by == 'admin'

        # Verify metadata fields
        assert model.metadata_json == {'data': 'value'}
        assert model.version == 1

        # Verify status fields
        assert model.status == 'processing'

    def test_full_model_to_dict(self, db_session):
        """Test full model to_dict includes all fields."""
        model = FullModel(
            name='full_test',
            created_by='user1',
            status='active'
        )

        db_session.add(model)
        db_session.commit()

        model_dict = model.to_dict()

        # Should have base model fields
        assert 'id' in model_dict
        assert 'created_at' in model_dict
        assert 'is_active' in model_dict
