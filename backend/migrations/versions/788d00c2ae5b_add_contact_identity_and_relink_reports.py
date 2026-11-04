"""add_contact_identity_and_relink_reports

Revision ID: 788d00c2ae5b
Revises: d1c8415c7093
Create Date: 2026-10-07
"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '788d00c2ae5b'
down_revision: Union[str, None] = 'd1c8415c7093'
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create contact_identities table
    op.create_table(
        'contact_identities',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('identity_type', sa.String(length=20), nullable=False),
        sa.Column('identity_value', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(
        'uq_identity_type_value',
        'contact_identities',
        ['identity_type', 'identity_value'],
        unique=True
    )

    # 2. Add nullable identity_id columns to contacts and reports
    op.add_column('contacts', sa.Column('identity_id', sa.Uuid(as_uuid=True), nullable=True))
    op.add_column('reports', sa.Column('identity_id', sa.Uuid(as_uuid=True), nullable=True))

    # 3. Data Backfill: Populate contact_identities from existing contacts
    connection = op.get_bind()
    existing_contacts = connection.execute(
        sa.text("SELECT id, contact_type, contact_value FROM contacts")
    ).fetchall()

    for contact in existing_contacts:
        c_id, c_type, c_val = contact[0], contact[1].lower().strip(), contact[2].strip()
        
        # Check if an identity record already exists
        existing_identity = connection.execute(
            sa.text("SELECT id FROM contact_identities WHERE identity_type = :t AND identity_value = :v"),
            {"t": c_type, "v": c_val}
        ).fetchone()

        if existing_identity:
            identity_id = existing_identity[0]
        else:
            identity_id = uuid.uuid4()
            connection.execute(
                sa.text("INSERT INTO contact_identities (id, identity_type, identity_value, created_at) VALUES (:id, :t, :v, now())"),
                {"id": identity_id, "t": c_type, "v": c_val}
            )

        # Link contact
        connection.execute(
            sa.text("UPDATE contacts SET identity_id = :ident_id WHERE id = :c_id"),
            {"ident_id": identity_id, "c_id": c_id}
        )

        # Link existing reports referencing this contact
        connection.execute(
            sa.text("UPDATE reports SET identity_id = :ident_id WHERE contact_id = :c_id"),
            {"ident_id": identity_id, "c_id": c_id}
        )

    # 4. Make columns non-nullable and apply Foreign Keys
    op.alter_column('contacts', 'identity_id', nullable=False)
    op.create_foreign_key(
        'fk_contacts_identity_id',
        'contacts',
        'contact_identities',
        ['identity_id'],
        ['id'],
        ondelete='RESTRICT'
    )

    op.alter_column('reports', 'identity_id', nullable=False)
    op.create_foreign_key(
        'fk_reports_identity_id',
        'reports',
        'contact_identities',
        ['identity_id'],
        ['id'],
        ondelete='RESTRICT'
    )

    # 5. Drop old foreign key and column from reports
    op.drop_constraint('reports_contact_id_fkey', 'reports', type_='foreignkey')
    op.drop_column('reports', 'contact_id')


def downgrade() -> None:
    # Re-add contact_id to reports
    op.add_column('reports', sa.Column('contact_id', sa.Uuid(as_uuid=True), nullable=True))
    
    # Backfill contact_id from identity
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE reports r
            SET contact_id = c.id
            FROM contacts c
            WHERE r.identity_id = c.identity_id
        """)
    )

    op.create_foreign_key('reports_contact_id_fkey', 'reports', 'contacts', ['contact_id'], ['id'], ondelete='CASCADE')
    op.alter_column('reports', 'contact_id', nullable=False)

    op.drop_constraint('fk_reports_identity_id', 'reports', type_='foreignkey')
    op.drop_column('reports', 'identity_id')

    op.drop_constraint('fk_contacts_identity_id', 'contacts', type_='foreignkey')
    op.drop_column('contacts', 'identity_id')

    op.drop_table('contact_identities')