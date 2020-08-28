# Copyright 2020 Cloudbase Solutions Srl
# All Rights Reserved.

import uuid

import sqlalchemy


def upgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine

    endpoint = sqlalchemy.Table(
        'endpoint', meta, autoload=True)
    base_transfer_action = sqlalchemy.Table(
        'base_transfer_action', meta, autoload=True)

    tables = []

    # add table for pool lifecycles:
    tables.append(
        sqlalchemy.Table(
            'minion_pool_lifecycle',
            meta,
            sqlalchemy.Column(
                "id", sqlalchemy.String(36),
                sqlalchemy.ForeignKey('base_transfer_action.base_id'),
                primary_key=True),
            sqlalchemy.Column(
                "pool_name", sqlalchemy.String(255), nullable=False),
            sqlalchemy.Column(
                "pool_status", sqlalchemy.String(255), nullable=False,
                default=lambda: "UNKNOWN"),
            sqlalchemy.Column(
                "pool_supporting_resources", sqlalchemy.Text, nullable=True),
            sqlalchemy.Column(
                'minimum_minions', sqlalchemy.Integer, nullable=False),
            sqlalchemy.Column(
                'maximum_minions', sqlalchemy.Integer, nullable=False),
            sqlalchemy.Column(
                'minion_max_idle_time', sqlalchemy.Integer, nullable=False),
            sqlalchemy.Column(
                'minion_retention_strategy', sqlalchemy.String(255),
                nullable=False)))

    # declare minion machine table:
    tables.append(
        sqlalchemy.Table(
            'minion_machine',
            meta,
            sqlalchemy.Column('id', sqlalchemy.String(36), primary_key=True,
                              default=lambda: str(uuid.uuid4())),
            sqlalchemy.Column(
                "user_id", sqlalchemy.String(255), nullable=False),
            sqlalchemy.Column(
                "project_id", sqlalchemy.String(255), nullable=False),
            sqlalchemy.Column('created_at', sqlalchemy.DateTime),
            sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
            sqlalchemy.Column('deleted_at', sqlalchemy.DateTime),
            sqlalchemy.Column('deleted', sqlalchemy.String(36)),
            sqlalchemy.Column(
                'pool_id', sqlalchemy.String(36),
                sqlalchemy.ForeignKey('minion_pool_lifecycle.id'), nullable=False),
            sqlalchemy.Column(
                'status', sqlalchemy.String(255), nullable=False,
                default=lambda: "UNKNOWN"),
            sqlalchemy.Column('connection_info', sqlalchemy.Text),
            sqlalchemy.Column('provider_properties', sqlalchemy.Text)))

    for index, table in enumerate(tables):
        try:
            table.create()
        except Exception:
            # If an error occurs, drop all tables created so far to return
            # to the previously existing state.
            meta.drop_all(tables=tables[:index])
            raise
