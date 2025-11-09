"""initial

Revision ID: edd12c4f2039
Revises:
Create Date: 2025-11-09 11:16:30.933239

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "edd12c4f2039"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "animes",
        sa.Column("mal_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title_ro", sa.String(), nullable=False),
        sa.Column("poster_url", sa.String(), nullable=False),
        sa.Column("poster_thumb_url", sa.String(), nullable=False),
        sa.Column("release_year", sa.Integer(), nullable=False),
        sa.Column("is_blacklisted", sa.Boolean(), nullable=False),
        sa.Column("is_finalized", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("mal_id", name=op.f("pk_animes")),
    )
    op.create_table(
        "anime_infos",
        sa.Column("anime_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["anime_id"], ["animes.mal_id"], name=op.f("fk_anime_infos_anime_id_animes")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anime_infos")),
    )
    op.create_table(
        "songs",
        sa.Column("anime_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.Enum("Opening", "Ending", name="category"), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("song_artist", sa.String(), nullable=False),
        sa.Column("song_name", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["anime_id"], ["animes.mal_id"], name=op.f("fk_songs_anime_id_animes")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_songs")),
        sa.UniqueConstraint("anime_id", "category", "number", name=op.f("uq_songs_anime_id")),
    )
    op.create_table(
        "levels",
        sa.Column("song_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("value >= 0 AND value <= 100", name=op.f("ck_levels__value_range")),
        sa.ForeignKeyConstraint(["song_id"], ["songs.id"], name=op.f("fk_levels_song_id_songs")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_levels")),
    )
    op.create_table(
        "sources",
        sa.Column("song_id", sa.Integer(), nullable=False),
        sa.Column("location", sa.JSON(), nullable=False),
        sa.Column("local_path", sa.String(), nullable=True),
        sa.Column("is_downloading", sa.Boolean(), nullable=False),
        sa.Column("is_invalid", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["song_id"], ["songs.id"], name=op.f("fk_sources_song_id_songs")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sources")),
    )
    op.create_table(
        "timings",
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("guess_start", sa.Float(), nullable=False),
        sa.Column("reveal_start", sa.Float(), nullable=False),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], name=op.f("fk_timings_source_id_sources")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_timings")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("timings")
    op.drop_table("sources")
    op.drop_table("levels")
    op.drop_table("songs")
    op.drop_table("anime_infos")
    op.drop_table("animes")
    sa.Enum("Opening", "Ending", name="category").drop(op.get_bind())
