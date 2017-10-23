# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, DateTime, Float, ForeignKey, Index, Integer, SmallInteger, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.types import LONGBLOB
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Acknowledge(Base):
    __tablename__ = 'acknowledges'

    acknowledgeid = Column(BigInteger, primary_key=True)
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), nullable=False, index=True)
    eventid = Column(ForeignKey(u'events.eventid', ondelete=u'CASCADE'), nullable=False, index=True)
    clock = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    message = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    event = relationship(u'Event')
    user = relationship(u'User')


class Action(Base):
    __tablename__ = 'actions'
    __table_args__ = (
        Index('actions_1', 'eventsource', 'status'),
    )

    actionid = Column(BigInteger, primary_key=True)
    name = Column(String(255, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    eventsource = Column(Integer, nullable=False, server_default=text("'0'"))
    evaltype = Column(Integer, nullable=False, server_default=text("'0'"))
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    esc_period = Column(Integer, nullable=False, server_default=text("'0'"))
    def_shortdata = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    def_longdata = Column(Text(collation=u'utf8_bin'), nullable=False)
    recovery_msg = Column(Integer, nullable=False, server_default=text("'0'"))
    r_shortdata = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    r_longdata = Column(Text(collation=u'utf8_bin'), nullable=False)
    formula = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))


class Alert(Base):
    __tablename__ = 'alerts'
    __table_args__ = (
        Index('alerts_4', 'status', 'retries'),
    )

    alertid = Column(BigInteger, primary_key=True)
    actionid = Column(ForeignKey(u'actions.actionid', ondelete=u'CASCADE'), nullable=False, index=True)
    eventid = Column(ForeignKey(u'events.eventid', ondelete=u'CASCADE'), nullable=False, index=True)
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), index=True)
    clock = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    mediatypeid = Column(ForeignKey(u'media_type.mediatypeid', ondelete=u'CASCADE'), index=True)
    sendto = Column(String(100, u'utf8_bin'), nullable=False, server_default=text("''"))
    subject = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    message = Column(Text(collation=u'utf8_bin'), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    retries = Column(Integer, nullable=False, server_default=text("'0'"))
    error = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    esc_step = Column(Integer, nullable=False, server_default=text("'0'"))
    alerttype = Column(Integer, nullable=False, server_default=text("'0'"))

    action = relationship(u'Action')
    event = relationship(u'Event')
    media_type = relationship(u'MediaType')
    user = relationship(u'User')


class ApplicationDiscovery(Base):
    __tablename__ = 'application_discovery'

    application_discoveryid = Column(BigInteger, primary_key=True)
    applicationid = Column(ForeignKey(u'applications.applicationid', ondelete=u'CASCADE'), nullable=False, index=True)
    application_prototypeid = Column(ForeignKey(u'application_prototype.application_prototypeid', ondelete=u'CASCADE'), nullable=False, index=True)
    name = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    lastcheck = Column(Integer, nullable=False, server_default=text("'0'"))
    ts_delete = Column(Integer, nullable=False, server_default=text("'0'"))

    application_prototype = relationship(u'ApplicationPrototype')
    application = relationship(u'Application')


class ApplicationPrototype(Base):
    __tablename__ = 'application_prototype'

    application_prototypeid = Column(BigInteger, primary_key=True)
    itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False, index=True)
    templateid = Column(ForeignKey(u'application_prototype.application_prototypeid', ondelete=u'CASCADE'), index=True)
    name = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    item = relationship(u'Item')
    parent = relationship(u'ApplicationPrototype', remote_side=[application_prototypeid])


class ApplicationTemplate(Base):
    __tablename__ = 'application_template'
    __table_args__ = (
        Index('application_template_1', 'applicationid', 'templateid', unique=True),
    )

    application_templateid = Column(BigInteger, primary_key=True)
    applicationid = Column(ForeignKey(u'applications.applicationid', ondelete=u'CASCADE'), nullable=False)
    templateid = Column(ForeignKey(u'applications.applicationid', ondelete=u'CASCADE'), nullable=False, index=True)

    application = relationship(u'Application', primaryjoin='ApplicationTemplate.applicationid == Application.applicationid')
    application1 = relationship(u'Application', primaryjoin='ApplicationTemplate.templateid == Application.applicationid')


class Application(Base):
    __tablename__ = 'applications'
    __table_args__ = (
        Index('applications_2', 'hostid', 'name', unique=True),
    )

    applicationid = Column(BigInteger, primary_key=True)
    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False)
    name = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    flags = Column(Integer, nullable=False, server_default=text("'0'"))

    host = relationship(u'Host')


class Auditlog(Base):
    __tablename__ = 'auditlog'
    __table_args__ = (
        Index('auditlog_1', 'userid', 'clock'),
    )

    auditid = Column(BigInteger, primary_key=True)
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), nullable=False)
    clock = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    action = Column(Integer, nullable=False, server_default=text("'0'"))
    resourcetype = Column(Integer, nullable=False, server_default=text("'0'"))
    details = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("'0'"))
    ip = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    resourceid = Column(BigInteger, nullable=False, server_default=text("'0'"))
    resourcename = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    user = relationship(u'User')


class AuditlogDetail(Base):
    __tablename__ = 'auditlog_details'

    auditdetailid = Column(BigInteger, primary_key=True)
    auditid = Column(ForeignKey(u'auditlog.auditid', ondelete=u'CASCADE'), nullable=False, index=True)
    table_name = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    field_name = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    oldvalue = Column(Text(collation=u'utf8_bin'), nullable=False)
    newvalue = Column(Text(collation=u'utf8_bin'), nullable=False)

    auditlog = relationship(u'Auditlog')


class AuthGroup(Base):
    __tablename__ = 'auth_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(80, u'utf8_bin'), nullable=False, unique=True)


class AuthGroupPermission(Base):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        Index('group_id', 'group_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey(u'auth_group.id'), nullable=False)
    permission_id = Column(ForeignKey(u'auth_permission.id'), nullable=False, index=True)

    group = relationship(u'AuthGroup')
    permission = relationship(u'AuthPermission')


class AuthPermission(Base):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        Index('content_type_id', 'content_type_id', 'codename', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255, u'utf8_bin'), nullable=False)
    content_type_id = Column(ForeignKey(u'django_content_type.id'), nullable=False)
    codename = Column(String(100, u'utf8_bin'), nullable=False)

    content_type = relationship(u'DjangoContentType')


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    password = Column(String(128, u'utf8_bin'), nullable=False)
    last_login = Column(DateTime)
    is_superuser = Column(Integer, nullable=False)
    username = Column(String(30, u'utf8_bin'), nullable=False, unique=True)
    first_name = Column(String(30, u'utf8_bin'), nullable=False)
    last_name = Column(String(30, u'utf8_bin'), nullable=False)
    email = Column(String(254, u'utf8_bin'), nullable=False)
    is_staff = Column(Integer, nullable=False)
    is_active = Column(Integer, nullable=False)
    date_joined = Column(DateTime, nullable=False)


class AuthUserGroup(Base):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        Index('user_id', 'user_id', 'group_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False)
    group_id = Column(ForeignKey(u'auth_group.id'), nullable=False, index=True)

    group = relationship(u'AuthGroup')
    user = relationship(u'AuthUser')


class AuthUserUserPermission(Base):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        Index('user_id', 'user_id', 'permission_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False)
    permission_id = Column(ForeignKey(u'auth_permission.id'), nullable=False, index=True)

    permission = relationship(u'AuthPermission')
    user = relationship(u'AuthUser')


class AutoregHost(Base):
    __tablename__ = 'autoreg_host'
    __table_args__ = (
        Index('autoreg_host_1', 'proxy_hostid', 'host'),
    )

    autoreg_hostid = Column(BigInteger, primary_key=True)
    proxy_hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'))
    host = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    listen_ip = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    listen_port = Column(Integer, nullable=False, server_default=text("'0'"))
    listen_dns = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    host_metadata = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    host1 = relationship(u'Host')


class CompileDailyServerUsage(Base):
    __tablename__ = 'compile_daily_server_usage'

    id = Column(BigInteger, primary_key=True)
    date = Column(Date, nullable=False)
    normal_usage_server_count = Column(Integer, nullable=False)
    low_usage_server_count = Column(Integer, nullable=False)
    nearly_no_usage_server_count = Column(Integer, nullable=False)
    high_usage_server_count = Column(Integer, nullable=False)
    region = Column(String(3, u'utf8_bin'), nullable=False)


class CompileServerUsageInfo(Base):
    __tablename__ = 'compile_server_usage_info'

    date = Column(Date)
    hostname = Column(String(255, u'utf8_bin'))
    owner = Column(String(255, u'utf8_bin'))
    ipaddress = Column(String(255, u'utf8_bin'))
    cpu_load_gt_50_coun = Column(Integer)
    total_memory = Column(String(255, u'utf8_bin'))
    total_CPU_cores = Column(Integer)
    largest_disk_mount_point = Column(String(255, u'utf8_bin'))
    total_diskspace = Column(String(255, u'utf8_bin'))
    used_diskspace = Column(String(255, u'utf8_bin'))
    disk_used_ratio = Column(Float(asdecimal=True))
    id = Column(BigInteger, primary_key=True)


class Condition(Base):
    __tablename__ = 'conditions'

    conditionid = Column(BigInteger, primary_key=True)
    actionid = Column(ForeignKey(u'actions.actionid', ondelete=u'CASCADE'), nullable=False, index=True)
    conditiontype = Column(Integer, nullable=False, server_default=text("'0'"))
    operator = Column(Integer, nullable=False, server_default=text("'0'"))
    value = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    action = relationship(u'Action')


class Config(Base):
    __tablename__ = 'config'

    configid = Column(BigInteger, primary_key=True)
    refresh_unsupported = Column(Integer, nullable=False, server_default=text("'0'"))
    work_period = Column(String(100, u'utf8_bin'), nullable=False, server_default=text("'1-5,00:00-24:00'"))
    alert_usrgrpid = Column(ForeignKey(u'usrgrp.usrgrpid'), index=True)
    event_ack_enable = Column(Integer, nullable=False, server_default=text("'1'"))
    event_expire = Column(Integer, nullable=False, server_default=text("'7'"))
    event_show_max = Column(Integer, nullable=False, server_default=text("'100'"))
    default_theme = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("'blue-theme'"))
    authentication_type = Column(Integer, nullable=False, server_default=text("'0'"))
    ldap_host = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    ldap_port = Column(Integer, nullable=False, server_default=text("'389'"))
    ldap_base_dn = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    ldap_bind_dn = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    ldap_bind_password = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    ldap_search_attribute = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    dropdown_first_entry = Column(Integer, nullable=False, server_default=text("'1'"))
    dropdown_first_remember = Column(Integer, nullable=False, server_default=text("'1'"))
    discovery_groupid = Column(ForeignKey(u'groups.groupid'), nullable=False, index=True)
    max_in_table = Column(Integer, nullable=False, server_default=text("'50'"))
    search_limit = Column(Integer, nullable=False, server_default=text("'1000'"))
    severity_color_0 = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'97AAB3'"))
    severity_color_1 = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'7499FF'"))
    severity_color_2 = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'FFC859'"))
    severity_color_3 = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'FFA059'"))
    severity_color_4 = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'E97659'"))
    severity_color_5 = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'E45959'"))
    severity_name_0 = Column(String(32, u'utf8_bin'), nullable=False, server_default=text("'Not classified'"))
    severity_name_1 = Column(String(32, u'utf8_bin'), nullable=False, server_default=text("'Information'"))
    severity_name_2 = Column(String(32, u'utf8_bin'), nullable=False, server_default=text("'Warning'"))
    severity_name_3 = Column(String(32, u'utf8_bin'), nullable=False, server_default=text("'Average'"))
    severity_name_4 = Column(String(32, u'utf8_bin'), nullable=False, server_default=text("'High'"))
    severity_name_5 = Column(String(32, u'utf8_bin'), nullable=False, server_default=text("'Disaster'"))
    ok_period = Column(Integer, nullable=False, server_default=text("'1800'"))
    blink_period = Column(Integer, nullable=False, server_default=text("'1800'"))
    problem_unack_color = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'DC0000'"))
    problem_ack_color = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'DC0000'"))
    ok_unack_color = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'00AA00'"))
    ok_ack_color = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'00AA00'"))
    problem_unack_style = Column(Integer, nullable=False, server_default=text("'1'"))
    problem_ack_style = Column(Integer, nullable=False, server_default=text("'1'"))
    ok_unack_style = Column(Integer, nullable=False, server_default=text("'1'"))
    ok_ack_style = Column(Integer, nullable=False, server_default=text("'1'"))
    snmptrap_logging = Column(Integer, nullable=False, server_default=text("'1'"))
    server_check_interval = Column(Integer, nullable=False, server_default=text("'10'"))
    hk_events_mode = Column(Integer, nullable=False, server_default=text("'1'"))
    hk_events_trigger = Column(Integer, nullable=False, server_default=text("'365'"))
    hk_events_internal = Column(Integer, nullable=False, server_default=text("'365'"))
    hk_events_discovery = Column(Integer, nullable=False, server_default=text("'365'"))
    hk_events_autoreg = Column(Integer, nullable=False, server_default=text("'365'"))
    hk_services_mode = Column(Integer, nullable=False, server_default=text("'1'"))
    hk_services = Column(Integer, nullable=False, server_default=text("'365'"))
    hk_audit_mode = Column(Integer, nullable=False, server_default=text("'1'"))
    hk_audit = Column(Integer, nullable=False, server_default=text("'365'"))
    hk_sessions_mode = Column(Integer, nullable=False, server_default=text("'1'"))
    hk_sessions = Column(Integer, nullable=False, server_default=text("'365'"))
    hk_history_mode = Column(Integer, nullable=False, server_default=text("'1'"))
    hk_history_global = Column(Integer, nullable=False, server_default=text("'0'"))
    hk_history = Column(Integer, nullable=False, server_default=text("'90'"))
    hk_trends_mode = Column(Integer, nullable=False, server_default=text("'1'"))
    hk_trends_global = Column(Integer, nullable=False, server_default=text("'0'"))
    hk_trends = Column(Integer, nullable=False, server_default=text("'365'"))
    default_inventory_mode = Column(Integer, nullable=False, server_default=text("'-1'"))

    usrgrp = relationship(u'Usrgrp')
    group = relationship(u'Group')


t_dbversion = Table(
    'dbversion', metadata,
    Column('mandatory', Integer, nullable=False, server_default=text("'0'")),
    Column('optional', Integer, nullable=False, server_default=text("'0'"))
)


class Dcheck(Base):
    __tablename__ = 'dchecks'

    dcheckid = Column(BigInteger, primary_key=True)
    druleid = Column(ForeignKey(u'drules.druleid', ondelete=u'CASCADE'), nullable=False, index=True)
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    key_ = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    snmp_community = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    ports = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("'0'"))
    snmpv3_securityname = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    snmpv3_securitylevel = Column(Integer, nullable=False, server_default=text("'0'"))
    snmpv3_authpassphrase = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    snmpv3_privpassphrase = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    uniq = Column(Integer, nullable=False, server_default=text("'0'"))
    snmpv3_authprotocol = Column(Integer, nullable=False, server_default=text("'0'"))
    snmpv3_privprotocol = Column(Integer, nullable=False, server_default=text("'0'"))
    snmpv3_contextname = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    drule = relationship(u'Drule')


class Dhost(Base):
    __tablename__ = 'dhosts'

    dhostid = Column(BigInteger, primary_key=True)
    druleid = Column(ForeignKey(u'drules.druleid', ondelete=u'CASCADE'), nullable=False, index=True)
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    lastup = Column(Integer, nullable=False, server_default=text("'0'"))
    lastdown = Column(Integer, nullable=False, server_default=text("'0'"))

    drule = relationship(u'Drule')


class DjangoAdminLog(Base):
    __tablename__ = 'django_admin_log'

    id = Column(Integer, primary_key=True)
    action_time = Column(DateTime, nullable=False)
    object_id = Column(String(collation=u'utf8_bin'))
    object_repr = Column(String(200, u'utf8_bin'), nullable=False)
    action_flag = Column(SmallInteger, nullable=False)
    change_message = Column(String(collation=u'utf8_bin'), nullable=False)
    content_type_id = Column(ForeignKey(u'django_content_type.id'), index=True)
    user_id = Column(ForeignKey(u'auth_user.id'), nullable=False, index=True)

    content_type = relationship(u'DjangoContentType')
    user = relationship(u'AuthUser')


class DjangoContentType(Base):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        Index('django_content_type_app_label_45f3b1d93ec8c61c_uniq', 'app_label', 'model', unique=True),
    )

    id = Column(Integer, primary_key=True)
    app_label = Column(String(100, u'utf8_bin'), nullable=False)
    model = Column(String(100, u'utf8_bin'), nullable=False)


class DjangoMigration(Base):
    __tablename__ = 'django_migrations'

    id = Column(Integer, primary_key=True)
    app = Column(String(255, u'utf8_bin'), nullable=False)
    name = Column(String(255, u'utf8_bin'), nullable=False)
    applied = Column(DateTime, nullable=False)


class DjangoSession(Base):
    __tablename__ = 'django_session'

    session_key = Column(String(40, u'utf8_bin'), primary_key=True)
    session_data = Column(String(collation=u'utf8_bin'), nullable=False)
    expire_date = Column(DateTime, nullable=False, index=True)


class Drule(Base):
    __tablename__ = 'drules'

    druleid = Column(BigInteger, primary_key=True)
    proxy_hostid = Column(ForeignKey(u'hosts.hostid'), index=True)
    name = Column(String(255, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    iprange = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))
    delay = Column(Integer, nullable=False, server_default=text("'3600'"))
    nextcheck = Column(Integer, nullable=False, server_default=text("'0'"))
    status = Column(Integer, nullable=False, server_default=text("'0'"))

    host = relationship(u'Host')


class Dservice(Base):
    __tablename__ = 'dservices'
    __table_args__ = (
        Index('dservices_1', 'dcheckid', 'type', 'key_', 'ip', 'port', unique=True),
    )

    dserviceid = Column(BigInteger, primary_key=True)
    dhostid = Column(ForeignKey(u'dhosts.dhostid', ondelete=u'CASCADE'), nullable=False, index=True)
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    key_ = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    value = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    port = Column(Integer, nullable=False, server_default=text("'0'"))
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    lastup = Column(Integer, nullable=False, server_default=text("'0'"))
    lastdown = Column(Integer, nullable=False, server_default=text("'0'"))
    dcheckid = Column(ForeignKey(u'dchecks.dcheckid', ondelete=u'CASCADE'), nullable=False)
    ip = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    dns = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))

    dcheck = relationship(u'Dcheck')
    dhost = relationship(u'Dhost')


class Escalation(Base):
    __tablename__ = 'escalations'
    __table_args__ = (
        Index('escalations_1', 'actionid', 'triggerid', 'itemid', 'escalationid', unique=True),
    )

    escalationid = Column(BigInteger, primary_key=True)
    actionid = Column(BigInteger, nullable=False)
    triggerid = Column(BigInteger)
    eventid = Column(BigInteger)
    r_eventid = Column(BigInteger)
    nextcheck = Column(Integer, nullable=False, server_default=text("'0'"))
    esc_step = Column(Integer, nullable=False, server_default=text("'0'"))
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    itemid = Column(BigInteger)


class Event(Base):
    __tablename__ = 'events'
    __table_args__ = (
        Index('events_1', 'source', 'object', 'objectid', 'clock'),
        Index('events_2', 'source', 'object', 'clock')
    )

    eventid = Column(BigInteger, primary_key=True)
    source = Column(Integer, nullable=False, server_default=text("'0'"))
    object = Column(Integer, nullable=False, server_default=text("'0'"))
    objectid = Column(BigInteger, nullable=False, server_default=text("'0'"))
    clock = Column(Integer, nullable=False, server_default=text("'0'"))
    value = Column(Integer, nullable=False, server_default=text("'0'"))
    acknowledged = Column(Integer, nullable=False, server_default=text("'0'"))
    ns = Column(Integer, nullable=False, server_default=text("'0'"))


class Expression(Base):
    __tablename__ = 'expressions'

    expressionid = Column(BigInteger, primary_key=True)
    regexpid = Column(ForeignKey(u'regexps.regexpid', ondelete=u'CASCADE'), nullable=False, index=True)
    expression = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    expression_type = Column(Integer, nullable=False, server_default=text("'0'"))
    exp_delimiter = Column(String(1, u'utf8_bin'), nullable=False, server_default=text("''"))
    case_sensitive = Column(Integer, nullable=False, server_default=text("'0'"))

    regexp = relationship(u'Regexp')


class Function(Base):
    __tablename__ = 'functions'
    __table_args__ = (
        Index('functions_2', 'itemid', 'function', 'parameter'),
    )

    functionid = Column(BigInteger, primary_key=True)
    itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False)
    triggerid = Column(ForeignKey(u'triggers.triggerid', ondelete=u'CASCADE'), nullable=False, index=True)
    function = Column(String(12, u'utf8_bin'), nullable=False, server_default=text("''"))
    parameter = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("'0'"))

    item = relationship(u'Item')
    trigger = relationship(u'Trigger')


class Globalmacro(Base):
    __tablename__ = 'globalmacro'

    globalmacroid = Column(BigInteger, primary_key=True)
    macro = Column(String(255, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    value = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))


class Globalvar(Base):
    __tablename__ = 'globalvars'

    globalvarid = Column(BigInteger, primary_key=True)
    snmp_lastsize = Column(Integer, nullable=False, server_default=text("'0'"))


t_graph_discovery = Table(
    'graph_discovery', metadata,
    Column('graphid', ForeignKey(u'graphs.graphid', ondelete=u'CASCADE'), primary_key=True),
    Column('parent_graphid', ForeignKey(u'graphs.graphid'), nullable=False, index=True)
)


class GraphTheme(Base):
    __tablename__ = 'graph_theme'

    graphthemeid = Column(BigInteger, primary_key=True)
    theme = Column(String(64, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    backgroundcolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))
    graphcolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))
    gridcolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))
    maingridcolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))
    gridbordercolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))
    textcolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))
    highlightcolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))
    leftpercentilecolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))
    rightpercentilecolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))
    nonworktimecolor = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("''"))


class Graph(Base):
    __tablename__ = 'graphs'

    graphid = Column(BigInteger, primary_key=True)
    name = Column(String(128, u'utf8_bin'), nullable=False, index=True, server_default=text("''"))
    width = Column(Integer, nullable=False, server_default=text("'900'"))
    height = Column(Integer, nullable=False, server_default=text("'200'"))
    yaxismin = Column(Float(16, True), nullable=False, server_default=text("'0.0000'"))
    yaxismax = Column(Float(16, True), nullable=False, server_default=text("'100.0000'"))
    templateid = Column(ForeignKey(u'graphs.graphid', ondelete=u'CASCADE'), index=True)
    show_work_period = Column(Integer, nullable=False, server_default=text("'1'"))
    show_triggers = Column(Integer, nullable=False, server_default=text("'1'"))
    graphtype = Column(Integer, nullable=False, server_default=text("'0'"))
    show_legend = Column(Integer, nullable=False, server_default=text("'1'"))
    show_3d = Column(Integer, nullable=False, server_default=text("'0'"))
    percent_left = Column(Float(16, True), nullable=False, server_default=text("'0.0000'"))
    percent_right = Column(Float(16, True), nullable=False, server_default=text("'0.0000'"))
    ymin_type = Column(Integer, nullable=False, server_default=text("'0'"))
    ymax_type = Column(Integer, nullable=False, server_default=text("'0'"))
    ymin_itemid = Column(ForeignKey(u'items.itemid'), index=True)
    ymax_itemid = Column(ForeignKey(u'items.itemid'), index=True)
    flags = Column(Integer, nullable=False, server_default=text("'0'"))

    parent = relationship(u'Graph', remote_side=[graphid])
    item = relationship(u'Item', primaryjoin='Graph.ymax_itemid == Item.itemid')
    item1 = relationship(u'Item', primaryjoin='Graph.ymin_itemid == Item.itemid')
    parents = relationship(
        u'Graph',
        secondary='graph_discovery',
        primaryjoin=u'Graph.graphid == graph_discovery.c.graphid',
        secondaryjoin=u'Graph.graphid == graph_discovery.c.parent_graphid'
    )


class GraphsItem(Base):
    __tablename__ = 'graphs_items'

    gitemid = Column(BigInteger, primary_key=True)
    graphid = Column(ForeignKey(u'graphs.graphid', ondelete=u'CASCADE'), nullable=False, index=True)
    itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False, index=True)
    drawtype = Column(Integer, nullable=False, server_default=text("'0'"))
    sortorder = Column(Integer, nullable=False, server_default=text("'0'"))
    color = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'009600'"))
    yaxisside = Column(Integer, nullable=False, server_default=text("'0'"))
    calc_fnc = Column(Integer, nullable=False, server_default=text("'2'"))
    type = Column(Integer, nullable=False, server_default=text("'0'"))

    graph = relationship(u'Graph')
    item = relationship(u'Item')


class GroupPrototype(Base):
    __tablename__ = 'group_prototype'

    group_prototypeid = Column(BigInteger, primary_key=True)
    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False, index=True)
    name = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    groupid = Column(ForeignKey(u'groups.groupid'), index=True)
    templateid = Column(ForeignKey(u'group_prototype.group_prototypeid', ondelete=u'CASCADE'), index=True)

    group = relationship(u'Group')
    host = relationship(u'Host')
    parent = relationship(u'GroupPrototype', remote_side=[group_prototypeid])


class Group(Base):
    __tablename__ = 'groups'

    groupid = Column(BigInteger, primary_key=True)
    name = Column(String(64, u'utf8_bin'), nullable=False, index=True, server_default=text("''"))
    internal = Column(Integer, nullable=False, server_default=text("'0'"))
    flags = Column(Integer, nullable=False, server_default=text("'0'"))


class GroupDiscovery(Base):
    __tablename__ = 'group_discovery'

    groupid = Column(ForeignKey(u'groups.groupid', ondelete=u'CASCADE'), primary_key=True)
    parent_group_prototypeid = Column(ForeignKey(u'group_prototype.group_prototypeid'), nullable=False, index=True)
    name = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    lastcheck = Column(Integer, nullable=False, server_default=text("'0'"))
    ts_delete = Column(Integer, nullable=False, server_default=text("'0'"))

    group_prototype = relationship(u'GroupPrototype')


t_history = Table(
    'history', metadata,
    Column('itemid', BigInteger, nullable=False),
    Column('clock', Integer, nullable=False, server_default=text("'0'")),
    Column('value', Float(16, True), nullable=False, server_default=text("'0.0000'")),
    Column('ns', Integer, nullable=False, server_default=text("'0'")),
    Index('history_1', 'itemid', 'clock')
)


class HistoryLog(Base):
    __tablename__ = 'history_log'
    __table_args__ = (
        Index('history_log_1', 'itemid', 'clock'),
        Index('history_log_2', 'itemid', 'id', unique=True)
    )

    id = Column(BigInteger, primary_key=True)
    itemid = Column(BigInteger, nullable=False)
    clock = Column(Integer, nullable=False, server_default=text("'0'"))
    timestamp = Column(Integer, nullable=False, server_default=text("'0'"))
    source = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    severity = Column(Integer, nullable=False, server_default=text("'0'"))
    value = Column(Text(collation=u'utf8_bin'), nullable=False)
    logeventid = Column(Integer, nullable=False, server_default=text("'0'"))
    ns = Column(Integer, nullable=False, server_default=text("'0'"))


t_history_str = Table(
    'history_str', metadata,
    Column('itemid', BigInteger, nullable=False),
    Column('clock', Integer, nullable=False, server_default=text("'0'")),
    Column('value', String(255, u'utf8_bin'), nullable=False, server_default=text("''")),
    Column('ns', Integer, nullable=False, server_default=text("'0'")),
    Index('history_str_1', 'itemid', 'clock')
)


class HistoryText(Base):
    __tablename__ = 'history_text'
    __table_args__ = (
        Index('history_text_2', 'itemid', 'id', unique=True),
        Index('history_text_1', 'itemid', 'clock')
    )

    id = Column(BigInteger, primary_key=True)
    itemid = Column(BigInteger, nullable=False)
    clock = Column(Integer, nullable=False, server_default=text("'0'"))
    value = Column(Text(collation=u'utf8_bin'), nullable=False)
    ns = Column(Integer, nullable=False, server_default=text("'0'"))


t_history_uint = Table(
    'history_uint', metadata,
    Column('itemid', BigInteger, nullable=False),
    Column('clock', Integer, nullable=False, server_default=text("'0'")),
    Column('value', BigInteger, nullable=False, server_default=text("'0'")),
    Column('ns', Integer, nullable=False, server_default=text("'0'")),
    Index('history_uint_1', 'itemid', 'clock')
)


class Hostmacro(Base):
    __tablename__ = 'hostmacro'
    __table_args__ = (
        Index('hostmacro_1', 'hostid', 'macro', unique=True),
    )

    hostmacroid = Column(BigInteger, primary_key=True)
    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False)
    macro = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    value = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    host = relationship(u'Host')


class Host(Base):
    __tablename__ = 'hosts'

    hostid = Column(BigInteger, primary_key=True)
    proxy_hostid = Column(ForeignKey(u'hosts.hostid'), index=True)
    host = Column(String(128, u'utf8_bin'), nullable=False, index=True, server_default=text("''"))
    status = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    disable_until = Column(Integer, nullable=False, server_default=text("'0'"))
    error = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))
    available = Column(Integer, nullable=False, server_default=text("'0'"))
    errors_from = Column(Integer, nullable=False, server_default=text("'0'"))
    lastaccess = Column(Integer, nullable=False, server_default=text("'0'"))
    ipmi_authtype = Column(Integer, nullable=False, server_default=text("'0'"))
    ipmi_privilege = Column(Integer, nullable=False, server_default=text("'2'"))
    ipmi_username = Column(String(16, u'utf8_bin'), nullable=False, server_default=text("''"))
    ipmi_password = Column(String(20, u'utf8_bin'), nullable=False, server_default=text("''"))
    ipmi_disable_until = Column(Integer, nullable=False, server_default=text("'0'"))
    ipmi_available = Column(Integer, nullable=False, server_default=text("'0'"))
    snmp_disable_until = Column(Integer, nullable=False, server_default=text("'0'"))
    snmp_available = Column(Integer, nullable=False, server_default=text("'0'"))
    maintenanceid = Column(ForeignKey(u'maintenances.maintenanceid'), index=True)
    maintenance_status = Column(Integer, nullable=False, server_default=text("'0'"))
    maintenance_type = Column(Integer, nullable=False, server_default=text("'0'"))
    maintenance_from = Column(Integer, nullable=False, server_default=text("'0'"))
    ipmi_errors_from = Column(Integer, nullable=False, server_default=text("'0'"))
    snmp_errors_from = Column(Integer, nullable=False, server_default=text("'0'"))
    ipmi_error = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))
    snmp_error = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))
    jmx_disable_until = Column(Integer, nullable=False, server_default=text("'0'"))
    jmx_available = Column(Integer, nullable=False, server_default=text("'0'"))
    jmx_errors_from = Column(Integer, nullable=False, server_default=text("'0'"))
    jmx_error = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))
    name = Column(String(128, u'utf8_bin'), nullable=False, index=True, server_default=text("''"))
    flags = Column(Integer, nullable=False, server_default=text("'0'"))
    templateid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), index=True)
    description = Column(Text(collation=u'utf8_bin'), nullable=False)
    tls_connect = Column(Integer, nullable=False, server_default=text("'1'"))
    tls_accept = Column(Integer, nullable=False, server_default=text("'1'"))
    tls_issuer = Column(String(1024, u'utf8_bin'), nullable=False, server_default=text("''"))
    tls_subject = Column(String(1024, u'utf8_bin'), nullable=False, server_default=text("''"))
    tls_psk_identity = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    tls_psk = Column(String(512, u'utf8_bin'), nullable=False, server_default=text("''"))

    maintenance = relationship(u'Maintenance')
    parent = relationship(u'Host', remote_side=[hostid], primaryjoin='Host.proxy_hostid == Host.hostid')
    parent1 = relationship(u'Host', remote_side=[hostid], primaryjoin='Host.templateid == Host.hostid')

class HostDiscovery(Base):
    __tablename__ = 'host_discovery'

    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), primary_key=True)
    parent_hostid = Column(ForeignKey(u'hosts.hostid'), index=True)
    parent_itemid = Column(ForeignKey(u'items.itemid'), index=True)
    host = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    lastcheck = Column(Integer, nullable=False, server_default=text("'0'"))
    ts_delete = Column(Integer, nullable=False, server_default=text("'0'"))

    host = relationship("Host", foreign_keys=[hostid])
    parent_host = relationship("Host",foreign_keys=[parent_hostid])
    item = relationship(u'Item')

    #host1 = relationship(u'Host', primaryjoin='HostDiscovery.parent_hostid == Host.hostid')


class HostInventory(Base):
    __tablename__ = 'host_inventory'

    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), primary_key=True)
    inventory_mode = Column(Integer, nullable=False, server_default=text("'0'"))
    type = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    type_full = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    name = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    alias = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    os = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    os_full = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    os_short = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    serialno_a = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    serialno_b = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    tag = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    asset_tag = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    macaddress_a = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    macaddress_b = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    hardware = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    hardware_full = Column(Text(collation=u'utf8_bin'), nullable=False)
    software = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    software_full = Column(Text(collation=u'utf8_bin'), nullable=False)
    software_app_a = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    software_app_b = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    software_app_c = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    software_app_d = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    software_app_e = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    contact = Column(Text(collation=u'utf8_bin'), nullable=False)
    location = Column(Text(collation=u'utf8_bin'), nullable=False)
    location_lat = Column(String(16, u'utf8_bin'), nullable=False, server_default=text("''"))
    location_lon = Column(String(16, u'utf8_bin'), nullable=False, server_default=text("''"))
    notes = Column(Text(collation=u'utf8_bin'), nullable=False)
    chassis = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    model = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    hw_arch = Column(String(32, u'utf8_bin'), nullable=False, server_default=text("''"))
    vendor = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    contract_number = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    installer_name = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    deployment_status = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    url_a = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    url_b = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    url_c = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    host_networks = Column(Text(collation=u'utf8_bin'), nullable=False)
    host_netmask = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    host_router = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    oob_ip = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    oob_netmask = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    oob_router = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    date_hw_purchase = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    date_hw_install = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    date_hw_expiry = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    date_hw_decomm = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    site_address_a = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    site_address_b = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    site_address_c = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    site_city = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    site_state = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    site_country = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    site_zip = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    site_rack = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    site_notes = Column(Text(collation=u'utf8_bin'), nullable=False)
    poc_1_name = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_1_email = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_1_phone_a = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_1_phone_b = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_1_cell = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_1_screen = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_1_notes = Column(Text(collation=u'utf8_bin'), nullable=False)
    poc_2_name = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_2_email = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_2_phone_a = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_2_phone_b = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_2_cell = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_2_screen = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    poc_2_notes = Column(Text(collation=u'utf8_bin'), nullable=False)

    host = relationship("Host", foreign_keys=[hostid])


class HostsGroup(Base):
    __tablename__ = 'hosts_groups'
    __table_args__ = (
        Index('hosts_groups_1', 'hostid', 'groupid', unique=True),
    )

    hostgroupid = Column(BigInteger, primary_key=True)
    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False)
    groupid = Column(ForeignKey(u'groups.groupid', ondelete=u'CASCADE'), nullable=False, index=True)

    group = relationship(u'Group')
    host = relationship(u'Host')


class HostsTemplate(Base):
    __tablename__ = 'hosts_templates'
    __table_args__ = (
        Index('hosts_templates_1', 'hostid', 'templateid', unique=True),
    )

    hosttemplateid = Column(BigInteger, primary_key=True)
    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False)
    templateid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False, index=True)

    host = relationship(u'Host', primaryjoin='HostsTemplate.hostid == Host.hostid')
    host1 = relationship(u'Host', primaryjoin='HostsTemplate.templateid == Host.hostid')


class Housekeeper(Base):
    __tablename__ = 'housekeeper'

    housekeeperid = Column(BigInteger, primary_key=True)
    tablename = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    field = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    value = Column(BigInteger, nullable=False)


class Httpstep(Base):
    __tablename__ = 'httpstep'

    httpstepid = Column(BigInteger, primary_key=True)
    httptestid = Column(ForeignKey(u'httptest.httptestid', ondelete=u'CASCADE'), nullable=False, index=True)
    name = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    no = Column(Integer, nullable=False, server_default=text("'0'"))
    url = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))
    timeout = Column(Integer, nullable=False, server_default=text("'15'"))
    posts = Column(Text(collation=u'utf8_bin'), nullable=False)
    required = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    status_codes = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    variables = Column(Text(collation=u'utf8_bin'), nullable=False)
    follow_redirects = Column(Integer, nullable=False, server_default=text("'1'"))
    retrieve_mode = Column(Integer, nullable=False, server_default=text("'0'"))
    headers = Column(Text(collation=u'utf8_bin'), nullable=False)

    httptest = relationship(u'Httptest')


class Httpstepitem(Base):
    __tablename__ = 'httpstepitem'
    __table_args__ = (
        Index('httpstepitem_1', 'httpstepid', 'itemid', unique=True),
    )

    httpstepitemid = Column(BigInteger, primary_key=True)
    httpstepid = Column(ForeignKey(u'httpstep.httpstepid', ondelete=u'CASCADE'), nullable=False)
    itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False, index=True)
    type = Column(Integer, nullable=False, server_default=text("'0'"))

    httpstep = relationship(u'Httpstep')
    item = relationship(u'Item')


class Httptest(Base):
    __tablename__ = 'httptest'
    __table_args__ = (
        Index('httptest_2', 'hostid', 'name', unique=True),
    )

    httptestid = Column(BigInteger, primary_key=True)
    name = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    applicationid = Column(ForeignKey(u'applications.applicationid'), index=True)
    nextcheck = Column(Integer, nullable=False, server_default=text("'0'"))
    delay = Column(Integer, nullable=False, server_default=text("'60'"))
    status = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    variables = Column(Text(collation=u'utf8_bin'), nullable=False)
    agent = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("'Zabbix'"))
    authentication = Column(Integer, nullable=False, server_default=text("'0'"))
    http_user = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    http_password = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False)
    templateid = Column(ForeignKey(u'httptest.httptestid', ondelete=u'CASCADE'), index=True)
    http_proxy = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    retries = Column(Integer, nullable=False, server_default=text("'1'"))
    ssl_cert_file = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    ssl_key_file = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    ssl_key_password = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    verify_peer = Column(Integer, nullable=False, server_default=text("'0'"))
    verify_host = Column(Integer, nullable=False, server_default=text("'0'"))
    headers = Column(Text(collation=u'utf8_bin'), nullable=False)

    application = relationship(u'Application')
    host = relationship(u'Host')
    parent = relationship(u'Httptest', remote_side=[httptestid])


class Httptestitem(Base):
    __tablename__ = 'httptestitem'
    __table_args__ = (
        Index('httptestitem_1', 'httptestid', 'itemid', unique=True),
    )

    httptestitemid = Column(BigInteger, primary_key=True)
    httptestid = Column(ForeignKey(u'httptest.httptestid', ondelete=u'CASCADE'), nullable=False)
    itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False, index=True)
    type = Column(Integer, nullable=False, server_default=text("'0'"))

    httptest = relationship(u'Httptest')
    item = relationship(u'Item')


class IconMap(Base):
    __tablename__ = 'icon_map'

    iconmapid = Column(BigInteger, primary_key=True)
    name = Column(String(64, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    default_iconid = Column(ForeignKey(u'images.imageid'), nullable=False, index=True)

    image = relationship(u'Image')


class IconMapping(Base):
    __tablename__ = 'icon_mapping'

    iconmappingid = Column(BigInteger, primary_key=True)
    iconmapid = Column(ForeignKey(u'icon_map.iconmapid', ondelete=u'CASCADE'), nullable=False, index=True)
    iconid = Column(ForeignKey(u'images.imageid'), nullable=False, index=True)
    inventory_link = Column(Integer, nullable=False, server_default=text("'0'"))
    expression = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    sortorder = Column(Integer, nullable=False, server_default=text("'0'"))

    image = relationship(u'Image')
    icon_map = relationship(u'IconMap')


class Id(Base):
    __tablename__ = 'ids'

    table_name = Column(String(64, u'utf8_bin'), primary_key=True, nullable=False, server_default=text("''"))
    field_name = Column(String(64, u'utf8_bin'), primary_key=True, nullable=False, server_default=text("''"))
    nextid = Column(BigInteger, nullable=False)


class Image(Base):
    __tablename__ = 'images'

    imageid = Column(BigInteger, primary_key=True)
    imagetype = Column(Integer, nullable=False, server_default=text("'0'"))
    name = Column(String(64, u'utf8_bin'), nullable=False, unique=True, server_default=text("'0'"))
    image = Column(LONGBLOB, nullable=False)


class Interface(Base):
    __tablename__ = 'interface'
    __table_args__ = (
        Index('interface_1', 'hostid', 'type'),
        Index('interface_2', 'ip', 'dns')
    )

    interfaceid = Column(BigInteger, primary_key=True)
    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False)
    main = Column(Integer, nullable=False, server_default=text("'0'"))
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    useip = Column(Integer, nullable=False, server_default=text("'1'"))
    ip = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("'127.0.0.1'"))
    dns = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    port = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("'10050'"))
    bulk = Column(Integer, nullable=False, server_default=text("'1'"))

    host = relationship(u'Host')
    parents = relationship(
        u'Interface',
        secondary='interface_discovery',
        primaryjoin=u'Interface.interfaceid == interface_discovery.c.interfaceid',
        secondaryjoin=u'Interface.interfaceid == interface_discovery.c.parent_interfaceid'
    )


t_interface_discovery = Table(
    'interface_discovery', metadata,
    Column('interfaceid', ForeignKey(u'interface.interfaceid', ondelete=u'CASCADE'), primary_key=True),
    Column('parent_interfaceid', ForeignKey(u'interface.interfaceid', ondelete=u'CASCADE'), nullable=False, index=True)
)


class ItemApplicationPrototype(Base):
    __tablename__ = 'item_application_prototype'
    __table_args__ = (
        Index('item_application_prototype_1', 'application_prototypeid', 'itemid', unique=True),
    )

    item_application_prototypeid = Column(BigInteger, primary_key=True)
    application_prototypeid = Column(ForeignKey(u'application_prototype.application_prototypeid', ondelete=u'CASCADE'), nullable=False)
    itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False, index=True)

    application_prototype = relationship(u'ApplicationPrototype')
    item = relationship(u'Item')


class ItemCondition(Base):
    __tablename__ = 'item_condition'

    item_conditionid = Column(BigInteger, primary_key=True)
    itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False, index=True)
    operator = Column(Integer, nullable=False, server_default=text("'8'"))
    macro = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    value = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    item = relationship(u'Item')


class ItemDiscovery(Base):
    __tablename__ = 'item_discovery'
    __table_args__ = (
        Index('item_discovery_1', 'itemid', 'parent_itemid', unique=True),
    )

    itemdiscoveryid = Column(BigInteger, primary_key=True)
    itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False)
    parent_itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False, index=True)
    key_ = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    lastcheck = Column(Integer, nullable=False, server_default=text("'0'"))
    ts_delete = Column(Integer, nullable=False, server_default=text("'0'"))

    item = relationship(u'Item', primaryjoin='ItemDiscovery.itemid == Item.itemid')
    item1 = relationship(u'Item', primaryjoin='ItemDiscovery.parent_itemid == Item.itemid')


class Item(Base):
    __tablename__ = 'items'
    __table_args__ = (
        Index('items_1', 'hostid', 'key_', unique=True),
    )

    itemid = Column(BigInteger, primary_key=True)
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    snmp_community = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    snmp_oid = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False)
    name = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    key_ = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    delay = Column(Integer, nullable=False, server_default=text("'0'"))
    history = Column(Integer, nullable=False, server_default=text("'90'"))
    trends = Column(Integer, nullable=False, server_default=text("'365'"))
    status = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    value_type = Column(Integer, nullable=False, server_default=text("'0'"))
    trapper_hosts = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    units = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    multiplier = Column(Integer, nullable=False, server_default=text("'0'"))
    delta = Column(Integer, nullable=False, server_default=text("'0'"))
    snmpv3_securityname = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    snmpv3_securitylevel = Column(Integer, nullable=False, server_default=text("'0'"))
    snmpv3_authpassphrase = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    snmpv3_privpassphrase = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    formula = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    error = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))
    lastlogsize = Column(BigInteger, nullable=False, server_default=text("'0'"))
    logtimefmt = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    templateid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), index=True)
    valuemapid = Column(ForeignKey(u'valuemaps.valuemapid'), index=True)
    delay_flex = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    params = Column(Text(collation=u'utf8_bin'), nullable=False)
    ipmi_sensor = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    data_type = Column(Integer, nullable=False, server_default=text("'0'"))
    authtype = Column(Integer, nullable=False, server_default=text("'0'"))
    username = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    password = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    publickey = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    privatekey = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    mtime = Column(Integer, nullable=False, server_default=text("'0'"))
    flags = Column(Integer, nullable=False, server_default=text("'0'"))
    interfaceid = Column(ForeignKey(u'interface.interfaceid'), index=True)
    port = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    description = Column(Text(collation=u'utf8_bin'), nullable=False)
    inventory_link = Column(Integer, nullable=False, server_default=text("'0'"))
    lifetime = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("'30'"))
    snmpv3_authprotocol = Column(Integer, nullable=False, server_default=text("'0'"))
    snmpv3_privprotocol = Column(Integer, nullable=False, server_default=text("'0'"))
    state = Column(Integer, nullable=False, server_default=text("'0'"))
    snmpv3_contextname = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    evaltype = Column(Integer, nullable=False, server_default=text("'0'"))

    host = relationship(u'Host')
    interface = relationship(u'Interface')
    parent = relationship(u'Item', remote_side=[itemid])
    valuemap = relationship(u'Valuemap')


class ItemsApplication(Base):
    __tablename__ = 'items_applications'
    __table_args__ = (
        Index('items_applications_1', 'applicationid', 'itemid', unique=True),
    )

    itemappid = Column(BigInteger, primary_key=True)
    applicationid = Column(ForeignKey(u'applications.applicationid', ondelete=u'CASCADE'), nullable=False)
    itemid = Column(ForeignKey(u'items.itemid', ondelete=u'CASCADE'), nullable=False, index=True)

    application = relationship(u'Application')
    item = relationship(u'Item')


class Maintenance(Base):
    __tablename__ = 'maintenances'
    __table_args__ = (
        Index('maintenances_1', 'active_since', 'active_till'),
    )

    maintenanceid = Column(BigInteger, primary_key=True)
    name = Column(String(128, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    maintenance_type = Column(Integer, nullable=False, server_default=text("'0'"))
    description = Column(Text(collation=u'utf8_bin'), nullable=False)
    active_since = Column(Integer, nullable=False, server_default=text("'0'"))
    active_till = Column(Integer, nullable=False, server_default=text("'0'"))


class MaintenancesGroup(Base):
    __tablename__ = 'maintenances_groups'
    __table_args__ = (
        Index('maintenances_groups_1', 'maintenanceid', 'groupid', unique=True),
    )

    maintenance_groupid = Column(BigInteger, primary_key=True)
    maintenanceid = Column(ForeignKey(u'maintenances.maintenanceid', ondelete=u'CASCADE'), nullable=False)
    groupid = Column(ForeignKey(u'groups.groupid', ondelete=u'CASCADE'), nullable=False, index=True)

    group = relationship(u'Group')
    maintenance = relationship(u'Maintenance')


class MaintenancesHost(Base):
    __tablename__ = 'maintenances_hosts'
    __table_args__ = (
        Index('maintenances_hosts_1', 'maintenanceid', 'hostid', unique=True),
    )

    maintenance_hostid = Column(BigInteger, primary_key=True)
    maintenanceid = Column(ForeignKey(u'maintenances.maintenanceid', ondelete=u'CASCADE'), nullable=False)
    hostid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), nullable=False, index=True)

    host = relationship(u'Host')
    maintenance = relationship(u'Maintenance')


class MaintenancesWindow(Base):
    __tablename__ = 'maintenances_windows'
    __table_args__ = (
        Index('maintenances_windows_1', 'maintenanceid', 'timeperiodid', unique=True),
    )

    maintenance_timeperiodid = Column(BigInteger, primary_key=True)
    maintenanceid = Column(ForeignKey(u'maintenances.maintenanceid', ondelete=u'CASCADE'), nullable=False)
    timeperiodid = Column(ForeignKey(u'timeperiods.timeperiodid', ondelete=u'CASCADE'), nullable=False, index=True)

    maintenance = relationship(u'Maintenance')
    timeperiod = relationship(u'Timeperiod')


class Mapping(Base):
    __tablename__ = 'mappings'

    mappingid = Column(BigInteger, primary_key=True)
    valuemapid = Column(ForeignKey(u'valuemaps.valuemapid', ondelete=u'CASCADE'), nullable=False, index=True)
    value = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    newvalue = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))

    valuemap = relationship(u'Valuemap')


class Media(Base):
    __tablename__ = 'media'

    mediaid = Column(BigInteger, primary_key=True)
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), nullable=False, index=True)
    mediatypeid = Column(ForeignKey(u'media_type.mediatypeid', ondelete=u'CASCADE'), nullable=False, index=True)
    sendto = Column(String(100, u'utf8_bin'), nullable=False, server_default=text("''"))
    active = Column(Integer, nullable=False, server_default=text("'0'"))
    severity = Column(Integer, nullable=False, server_default=text("'63'"))
    period = Column(String(100, u'utf8_bin'), nullable=False, server_default=text("'1-7,00:00-24:00'"))

    media_type = relationship(u'MediaType')
    user = relationship(u'User')


class MediaType(Base):
    __tablename__ = 'media_type'

    mediatypeid = Column(BigInteger, primary_key=True)
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    description = Column(String(100, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    smtp_server = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    smtp_helo = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    smtp_email = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    exec_path = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    gsm_modem = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    username = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    passwd = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    smtp_port = Column(Integer, nullable=False, server_default=text("'25'"))
    smtp_security = Column(Integer, nullable=False, server_default=text("'0'"))
    smtp_verify_peer = Column(Integer, nullable=False, server_default=text("'0'"))
    smtp_verify_host = Column(Integer, nullable=False, server_default=text("'0'"))
    smtp_authentication = Column(Integer, nullable=False, server_default=text("'0'"))
    exec_params = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))


class OpcommandGrp(Base):
    __tablename__ = 'opcommand_grp'

    opcommand_grpid = Column(BigInteger, primary_key=True)
    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), nullable=False, index=True)
    groupid = Column(ForeignKey(u'groups.groupid'), nullable=False, index=True)

    group = relationship(u'Group')
    operation = relationship(u'Operation')


class OpcommandHst(Base):
    __tablename__ = 'opcommand_hst'

    opcommand_hstid = Column(BigInteger, primary_key=True)
    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), nullable=False, index=True)
    hostid = Column(ForeignKey(u'hosts.hostid'), index=True)

    host = relationship(u'Host')
    operation = relationship(u'Operation')


class Opcondition(Base):
    __tablename__ = 'opconditions'

    opconditionid = Column(BigInteger, primary_key=True)
    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), nullable=False, index=True)
    conditiontype = Column(Integer, nullable=False, server_default=text("'0'"))
    operator = Column(Integer, nullable=False, server_default=text("'0'"))
    value = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    operation = relationship(u'Operation')


class Operation(Base):
    __tablename__ = 'operations'

    operationid = Column(BigInteger, primary_key=True)
    actionid = Column(ForeignKey(u'actions.actionid', ondelete=u'CASCADE'), nullable=False, index=True)
    operationtype = Column(Integer, nullable=False, server_default=text("'0'"))
    esc_period = Column(Integer, nullable=False, server_default=text("'0'"))
    esc_step_from = Column(Integer, nullable=False, server_default=text("'1'"))
    esc_step_to = Column(Integer, nullable=False, server_default=text("'1'"))
    evaltype = Column(Integer, nullable=False, server_default=text("'0'"))

    action = relationship(u'Action')


class Opinventory(Operation):
    __tablename__ = 'opinventory'

    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), primary_key=True)
    inventory_mode = Column(Integer, nullable=False, server_default=text("'0'"))


class Opcommand(Operation):
    __tablename__ = 'opcommand'

    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), primary_key=True)
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    scriptid = Column(ForeignKey(u'scripts.scriptid'), index=True)
    execute_on = Column(Integer, nullable=False, server_default=text("'0'"))
    port = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    authtype = Column(Integer, nullable=False, server_default=text("'0'"))
    username = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    password = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    publickey = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    privatekey = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    command = Column(Text(collation=u'utf8_bin'), nullable=False)

    script = relationship(u'Script')


class Opmessage(Operation):
    __tablename__ = 'opmessage'

    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), primary_key=True)
    default_msg = Column(Integer, nullable=False, server_default=text("'0'"))
    subject = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    message = Column(Text(collation=u'utf8_bin'), nullable=False)
    mediatypeid = Column(ForeignKey(u'media_type.mediatypeid'), index=True)

    media_type = relationship(u'MediaType')


class Opgroup(Base):
    __tablename__ = 'opgroup'
    __table_args__ = (
        Index('opgroup_1', 'operationid', 'groupid', unique=True),
    )

    opgroupid = Column(BigInteger, primary_key=True)
    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), nullable=False)
    groupid = Column(ForeignKey(u'groups.groupid'), nullable=False, index=True)

    group = relationship(u'Group')
    operation = relationship(u'Operation')


class OpmessageGrp(Base):
    __tablename__ = 'opmessage_grp'
    __table_args__ = (
        Index('opmessage_grp_1', 'operationid', 'usrgrpid', unique=True),
    )

    opmessage_grpid = Column(BigInteger, primary_key=True)
    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), nullable=False)
    usrgrpid = Column(ForeignKey(u'usrgrp.usrgrpid'), nullable=False, index=True)

    operation = relationship(u'Operation')
    usrgrp = relationship(u'Usrgrp')


class OpmessageUsr(Base):
    __tablename__ = 'opmessage_usr'
    __table_args__ = (
        Index('opmessage_usr_1', 'operationid', 'userid', unique=True),
    )

    opmessage_usrid = Column(BigInteger, primary_key=True)
    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), nullable=False)
    userid = Column(ForeignKey(u'users.userid'), nullable=False, index=True)

    operation = relationship(u'Operation')
    user = relationship(u'User')


class Optemplate(Base):
    __tablename__ = 'optemplate'
    __table_args__ = (
        Index('optemplate_1', 'operationid', 'templateid', unique=True),
    )

    optemplateid = Column(BigInteger, primary_key=True)
    operationid = Column(ForeignKey(u'operations.operationid', ondelete=u'CASCADE'), nullable=False)
    templateid = Column(ForeignKey(u'hosts.hostid'), nullable=False, index=True)

    operation = relationship(u'Operation')
    host = relationship(u'Host')


class Profile(Base):
    __tablename__ = 'profiles'
    __table_args__ = (
        Index('profiles_1', 'userid', 'idx', 'idx2'),
        Index('profiles_2', 'userid', 'profileid')
    )

    profileid = Column(BigInteger, primary_key=True)
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), nullable=False)
    idx = Column(String(96, u'utf8_bin'), nullable=False, server_default=text("''"))
    idx2 = Column(BigInteger, nullable=False, server_default=text("'0'"))
    value_id = Column(BigInteger, nullable=False, server_default=text("'0'"))
    value_int = Column(Integer, nullable=False, server_default=text("'0'"))
    value_str = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    source = Column(String(96, u'utf8_bin'), nullable=False, server_default=text("''"))
    type = Column(Integer, nullable=False, server_default=text("'0'"))

    user = relationship(u'User')


class ProxyAutoregHost(Base):
    __tablename__ = 'proxy_autoreg_host'

    id = Column(BigInteger, primary_key=True)
    clock = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    host = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    listen_ip = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    listen_port = Column(Integer, nullable=False, server_default=text("'0'"))
    listen_dns = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    host_metadata = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))


class ProxyDhistory(Base):
    __tablename__ = 'proxy_dhistory'

    id = Column(BigInteger, primary_key=True)
    clock = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    druleid = Column(BigInteger, nullable=False)
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    ip = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    port = Column(Integer, nullable=False, server_default=text("'0'"))
    key_ = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    value = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    dcheckid = Column(BigInteger)
    dns = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))


class ProxyHistory(Base):
    __tablename__ = 'proxy_history'

    id = Column(BigInteger, primary_key=True)
    itemid = Column(BigInteger, nullable=False)
    clock = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    timestamp = Column(Integer, nullable=False, server_default=text("'0'"))
    source = Column(String(64, u'utf8_bin'), nullable=False, server_default=text("''"))
    severity = Column(Integer, nullable=False, server_default=text("'0'"))
    value = Column(String(collation=u'utf8_bin'), nullable=False)
    logeventid = Column(Integer, nullable=False, server_default=text("'0'"))
    ns = Column(Integer, nullable=False, server_default=text("'0'"))
    state = Column(Integer, nullable=False, server_default=text("'0'"))
    lastlogsize = Column(BigInteger, nullable=False, server_default=text("'0'"))
    mtime = Column(Integer, nullable=False, server_default=text("'0'"))
    flags = Column(Integer, nullable=False, server_default=text("'0'"))


class Regexp(Base):
    __tablename__ = 'regexps'

    regexpid = Column(BigInteger, primary_key=True)
    name = Column(String(128, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    test_string = Column(Text(collation=u'utf8_bin'), nullable=False)


class Right(Base):
    __tablename__ = 'rights'

    rightid = Column(BigInteger, primary_key=True)
    groupid = Column(ForeignKey(u'usrgrp.usrgrpid', ondelete=u'CASCADE'), nullable=False, index=True)
    permission = Column(Integer, nullable=False, server_default=text("'0'"))
    id = Column(ForeignKey(u'groups.groupid', ondelete=u'CASCADE'), nullable=False, index=True)

    usrgrp = relationship(u'Usrgrp')
    group = relationship(u'Group')



class ScreenUser(Base):
    __tablename__ = 'screen_user'
    __table_args__ = (
        Index('screen_user_1', 'screenid', 'userid', unique=True),
    )

    screenuserid = Column(BigInteger, primary_key=True)
    screenid = Column(ForeignKey(u'screens.screenid', ondelete=u'CASCADE'), nullable=False)
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), nullable=False, index=True)
    permission = Column(Integer, nullable=False, server_default=text("'2'"))

    screen = relationship(u'Screen')
    user = relationship(u'User')


class ScreenUsrgrp(Base):
    __tablename__ = 'screen_usrgrp'
    __table_args__ = (
        Index('screen_usrgrp_1', 'screenid', 'usrgrpid', unique=True),
    )

    screenusrgrpid = Column(BigInteger, primary_key=True)
    screenid = Column(ForeignKey(u'screens.screenid', ondelete=u'CASCADE'), nullable=False)
    usrgrpid = Column(ForeignKey(u'usrgrp.usrgrpid', ondelete=u'CASCADE'), nullable=False, index=True)
    permission = Column(Integer, nullable=False, server_default=text("'2'"))

    screen = relationship(u'Screen')
    usrgrp = relationship(u'Usrgrp')


class Screen(Base):
    __tablename__ = 'screens'

    screenid = Column(BigInteger, primary_key=True)
    name = Column(String(255, u'utf8_bin'), nullable=False)
    hsize = Column(Integer, nullable=False, server_default=text("'1'"))
    vsize = Column(Integer, nullable=False, server_default=text("'1'"))
    templateid = Column(ForeignKey(u'hosts.hostid', ondelete=u'CASCADE'), index=True)
    userid = Column(ForeignKey(u'users.userid'), index=True)
    private = Column(Integer, nullable=False, server_default=text("'1'"))

    host = relationship(u'Host')
    user = relationship(u'User')


class ScreensItem(Base):
    __tablename__ = 'screens_items'

    screenitemid = Column(BigInteger, primary_key=True)
    screenid = Column(ForeignKey(u'screens.screenid', ondelete=u'CASCADE'), nullable=False, index=True)
    resourcetype = Column(Integer, nullable=False, server_default=text("'0'"))
    resourceid = Column(BigInteger, nullable=False, server_default=text("'0'"))
    width = Column(Integer, nullable=False, server_default=text("'320'"))
    height = Column(Integer, nullable=False, server_default=text("'200'"))
    x = Column(Integer, nullable=False, server_default=text("'0'"))
    y = Column(Integer, nullable=False, server_default=text("'0'"))
    colspan = Column(Integer, nullable=False, server_default=text("'1'"))
    rowspan = Column(Integer, nullable=False, server_default=text("'1'"))
    elements = Column(Integer, nullable=False, server_default=text("'25'"))
    valign = Column(Integer, nullable=False, server_default=text("'0'"))
    halign = Column(Integer, nullable=False, server_default=text("'0'"))
    style = Column(Integer, nullable=False, server_default=text("'0'"))
    url = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    dynamic = Column(Integer, nullable=False, server_default=text("'0'"))
    sort_triggers = Column(Integer, nullable=False, server_default=text("'0'"))
    application = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    max_columns = Column(Integer, nullable=False, server_default=text("'3'"))

    screen = relationship(u'Screen')


class Script(Base):
    __tablename__ = 'scripts'

    scriptid = Column(BigInteger, primary_key=True)
    name = Column(String(255, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    command = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    host_access = Column(Integer, nullable=False, server_default=text("'2'"))
    usrgrpid = Column(ForeignKey(u'usrgrp.usrgrpid'), index=True)
    groupid = Column(ForeignKey(u'groups.groupid'), index=True)
    description = Column(Text(collation=u'utf8_bin'), nullable=False)
    confirmation = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    execute_on = Column(Integer, nullable=False, server_default=text("'1'"))

    group = relationship(u'Group')
    usrgrp = relationship(u'Usrgrp')


class ServiceAlarm(Base):
    __tablename__ = 'service_alarms'
    __table_args__ = (
        Index('service_alarms_1', 'serviceid', 'clock'),
    )

    servicealarmid = Column(BigInteger, primary_key=True)
    serviceid = Column(ForeignKey(u'services.serviceid', ondelete=u'CASCADE'), nullable=False)
    clock = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    value = Column(Integer, nullable=False, server_default=text("'0'"))

    service = relationship(u'Service')


class Service(Base):
    __tablename__ = 'services'

    serviceid = Column(BigInteger, primary_key=True)
    name = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    algorithm = Column(Integer, nullable=False, server_default=text("'0'"))
    triggerid = Column(ForeignKey(u'triggers.triggerid', ondelete=u'CASCADE'), index=True)
    showsla = Column(Integer, nullable=False, server_default=text("'0'"))
    goodsla = Column(Float(16, True), nullable=False, server_default=text("'99.9000'"))
    sortorder = Column(Integer, nullable=False, server_default=text("'0'"))

    trigger = relationship(u'Trigger')


class ServicesLink(Base):
    __tablename__ = 'services_links'
    __table_args__ = (
        Index('services_links_2', 'serviceupid', 'servicedownid', unique=True),
    )

    linkid = Column(BigInteger, primary_key=True)
    serviceupid = Column(ForeignKey(u'services.serviceid', ondelete=u'CASCADE'), nullable=False)
    servicedownid = Column(ForeignKey(u'services.serviceid', ondelete=u'CASCADE'), nullable=False, index=True)
    soft = Column(Integer, nullable=False, server_default=text("'0'"))

    service = relationship(u'Service', primaryjoin='ServicesLink.servicedownid == Service.serviceid')
    service1 = relationship(u'Service', primaryjoin='ServicesLink.serviceupid == Service.serviceid')


class ServicesTime(Base):
    __tablename__ = 'services_times'
    __table_args__ = (
        Index('services_times_1', 'serviceid', 'type', 'ts_from', 'ts_to'),
    )

    timeid = Column(BigInteger, primary_key=True)
    serviceid = Column(ForeignKey(u'services.serviceid', ondelete=u'CASCADE'), nullable=False)
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    ts_from = Column(Integer, nullable=False, server_default=text("'0'"))
    ts_to = Column(Integer, nullable=False, server_default=text("'0'"))
    note = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    service = relationship(u'Service')


class Session(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        Index('sessions_1', 'userid', 'status'),
    )

    sessionid = Column(String(32, u'utf8_bin'), primary_key=True, server_default=text("''"))
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), nullable=False)
    lastaccess = Column(Integer, nullable=False, server_default=text("'0'"))
    status = Column(Integer, nullable=False, server_default=text("'0'"))

    user = relationship(u'User')


class Slide(Base):
    __tablename__ = 'slides'

    slideid = Column(BigInteger, primary_key=True)
    slideshowid = Column(ForeignKey(u'slideshows.slideshowid', ondelete=u'CASCADE'), nullable=False, index=True)
    screenid = Column(ForeignKey(u'screens.screenid', ondelete=u'CASCADE'), nullable=False, index=True)
    step = Column(Integer, nullable=False, server_default=text("'0'"))
    delay = Column(Integer, nullable=False, server_default=text("'0'"))

    screen = relationship(u'Screen')
    slideshow = relationship(u'Slideshow')


class SlideshowUser(Base):
    __tablename__ = 'slideshow_user'
    __table_args__ = (
        Index('slideshow_user_1', 'slideshowid', 'userid', unique=True),
    )

    slideshowuserid = Column(BigInteger, primary_key=True)
    slideshowid = Column(ForeignKey(u'slideshows.slideshowid', ondelete=u'CASCADE'), nullable=False)
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), nullable=False, index=True)
    permission = Column(Integer, nullable=False, server_default=text("'2'"))

    slideshow = relationship(u'Slideshow')
    user = relationship(u'User')


class SlideshowUsrgrp(Base):
    __tablename__ = 'slideshow_usrgrp'
    __table_args__ = (
        Index('slideshow_usrgrp_1', 'slideshowid', 'usrgrpid', unique=True),
    )

    slideshowusrgrpid = Column(BigInteger, primary_key=True)
    slideshowid = Column(ForeignKey(u'slideshows.slideshowid', ondelete=u'CASCADE'), nullable=False)
    usrgrpid = Column(ForeignKey(u'usrgrp.usrgrpid', ondelete=u'CASCADE'), nullable=False, index=True)
    permission = Column(Integer, nullable=False, server_default=text("'2'"))

    slideshow = relationship(u'Slideshow')
    usrgrp = relationship(u'Usrgrp')


class Slideshow(Base):
    __tablename__ = 'slideshows'

    slideshowid = Column(BigInteger, primary_key=True)
    name = Column(String(255, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    delay = Column(Integer, nullable=False, server_default=text("'0'"))
    userid = Column(ForeignKey(u'users.userid'), nullable=False, index=True)
    private = Column(Integer, nullable=False, server_default=text("'1'"))

    user = relationship(u'User')


class SysmapElementUrl(Base):
    __tablename__ = 'sysmap_element_url'
    __table_args__ = (
        Index('sysmap_element_url_1', 'selementid', 'name', unique=True),
    )

    sysmapelementurlid = Column(BigInteger, primary_key=True)
    selementid = Column(ForeignKey(u'sysmaps_elements.selementid', ondelete=u'CASCADE'), nullable=False)
    name = Column(String(255, u'utf8_bin'), nullable=False)
    url = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    sysmaps_element = relationship(u'SysmapsElement')


class SysmapUrl(Base):
    __tablename__ = 'sysmap_url'
    __table_args__ = (
        Index('sysmap_url_1', 'sysmapid', 'name', unique=True),
    )

    sysmapurlid = Column(BigInteger, primary_key=True)
    sysmapid = Column(ForeignKey(u'sysmaps.sysmapid', ondelete=u'CASCADE'), nullable=False)
    name = Column(String(255, u'utf8_bin'), nullable=False)
    url = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    elementtype = Column(Integer, nullable=False, server_default=text("'0'"))

    sysmap = relationship(u'Sysmap')


class SysmapUser(Base):
    __tablename__ = 'sysmap_user'
    __table_args__ = (
        Index('sysmap_user_1', 'sysmapid', 'userid', unique=True),
    )

    sysmapuserid = Column(BigInteger, primary_key=True)
    sysmapid = Column(ForeignKey(u'sysmaps.sysmapid', ondelete=u'CASCADE'), nullable=False)
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), nullable=False, index=True)
    permission = Column(Integer, nullable=False, server_default=text("'2'"))

    sysmap = relationship(u'Sysmap')
    user = relationship(u'User')


class SysmapUsrgrp(Base):
    __tablename__ = 'sysmap_usrgrp'
    __table_args__ = (
        Index('sysmap_usrgrp_1', 'sysmapid', 'usrgrpid', unique=True),
    )

    sysmapusrgrpid = Column(BigInteger, primary_key=True)
    sysmapid = Column(ForeignKey(u'sysmaps.sysmapid', ondelete=u'CASCADE'), nullable=False)
    usrgrpid = Column(ForeignKey(u'usrgrp.usrgrpid', ondelete=u'CASCADE'), nullable=False, index=True)
    permission = Column(Integer, nullable=False, server_default=text("'2'"))

    sysmap = relationship(u'Sysmap')
    usrgrp = relationship(u'Usrgrp')


class Sysmap(Base):
    __tablename__ = 'sysmaps'

    sysmapid = Column(BigInteger, primary_key=True)
    name = Column(String(128, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    width = Column(Integer, nullable=False, server_default=text("'600'"))
    height = Column(Integer, nullable=False, server_default=text("'400'"))
    backgroundid = Column(ForeignKey(u'images.imageid'), index=True)
    label_type = Column(Integer, nullable=False, server_default=text("'2'"))
    label_location = Column(Integer, nullable=False, server_default=text("'0'"))
    highlight = Column(Integer, nullable=False, server_default=text("'1'"))
    expandproblem = Column(Integer, nullable=False, server_default=text("'1'"))
    markelements = Column(Integer, nullable=False, server_default=text("'0'"))
    show_unack = Column(Integer, nullable=False, server_default=text("'0'"))
    grid_size = Column(Integer, nullable=False, server_default=text("'50'"))
    grid_show = Column(Integer, nullable=False, server_default=text("'1'"))
    grid_align = Column(Integer, nullable=False, server_default=text("'1'"))
    label_format = Column(Integer, nullable=False, server_default=text("'0'"))
    label_type_host = Column(Integer, nullable=False, server_default=text("'2'"))
    label_type_hostgroup = Column(Integer, nullable=False, server_default=text("'2'"))
    label_type_trigger = Column(Integer, nullable=False, server_default=text("'2'"))
    label_type_map = Column(Integer, nullable=False, server_default=text("'2'"))
    label_type_image = Column(Integer, nullable=False, server_default=text("'2'"))
    label_string_host = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    label_string_hostgroup = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    label_string_trigger = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    label_string_map = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    label_string_image = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    iconmapid = Column(ForeignKey(u'icon_map.iconmapid'), index=True)
    expand_macros = Column(Integer, nullable=False, server_default=text("'0'"))
    severity_min = Column(Integer, nullable=False, server_default=text("'0'"))
    userid = Column(ForeignKey(u'users.userid'), nullable=False, index=True)
    private = Column(Integer, nullable=False, server_default=text("'1'"))

    image = relationship(u'Image')
    icon_map = relationship(u'IconMap')
    user = relationship(u'User')


class SysmapsElement(Base):
    __tablename__ = 'sysmaps_elements'

    selementid = Column(BigInteger, primary_key=True)
    sysmapid = Column(ForeignKey(u'sysmaps.sysmapid', ondelete=u'CASCADE'), nullable=False, index=True)
    elementid = Column(BigInteger, nullable=False, server_default=text("'0'"))
    elementtype = Column(Integer, nullable=False, server_default=text("'0'"))
    iconid_off = Column(ForeignKey(u'images.imageid'), index=True)
    iconid_on = Column(ForeignKey(u'images.imageid'), index=True)
    label = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))
    label_location = Column(Integer, nullable=False, server_default=text("'-1'"))
    x = Column(Integer, nullable=False, server_default=text("'0'"))
    y = Column(Integer, nullable=False, server_default=text("'0'"))
    iconid_disabled = Column(ForeignKey(u'images.imageid'), index=True)
    iconid_maintenance = Column(ForeignKey(u'images.imageid'), index=True)
    elementsubtype = Column(Integer, nullable=False, server_default=text("'0'"))
    areatype = Column(Integer, nullable=False, server_default=text("'0'"))
    width = Column(Integer, nullable=False, server_default=text("'200'"))
    height = Column(Integer, nullable=False, server_default=text("'200'"))
    viewtype = Column(Integer, nullable=False, server_default=text("'0'"))
    use_iconmap = Column(Integer, nullable=False, server_default=text("'1'"))
    application = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))

    image = relationship(u'Image', primaryjoin='SysmapsElement.iconid_disabled == Image.imageid')
    image1 = relationship(u'Image', primaryjoin='SysmapsElement.iconid_maintenance == Image.imageid')
    image2 = relationship(u'Image', primaryjoin='SysmapsElement.iconid_off == Image.imageid')
    image3 = relationship(u'Image', primaryjoin='SysmapsElement.iconid_on == Image.imageid')
    sysmap = relationship(u'Sysmap')


class SysmapsLinkTrigger(Base):
    __tablename__ = 'sysmaps_link_triggers'
    __table_args__ = (
        Index('sysmaps_link_triggers_1', 'linkid', 'triggerid', unique=True),
    )

    linktriggerid = Column(BigInteger, primary_key=True)
    linkid = Column(ForeignKey(u'sysmaps_links.linkid', ondelete=u'CASCADE'), nullable=False)
    triggerid = Column(ForeignKey(u'triggers.triggerid', ondelete=u'CASCADE'), nullable=False, index=True)
    drawtype = Column(Integer, nullable=False, server_default=text("'0'"))
    color = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'000000'"))

    sysmaps_link = relationship(u'SysmapsLink')
    trigger = relationship(u'Trigger')


class SysmapsLink(Base):
    __tablename__ = 'sysmaps_links'

    linkid = Column(BigInteger, primary_key=True)
    sysmapid = Column(ForeignKey(u'sysmaps.sysmapid', ondelete=u'CASCADE'), nullable=False, index=True)
    selementid1 = Column(ForeignKey(u'sysmaps_elements.selementid', ondelete=u'CASCADE'), nullable=False, index=True)
    selementid2 = Column(ForeignKey(u'sysmaps_elements.selementid', ondelete=u'CASCADE'), nullable=False, index=True)
    drawtype = Column(Integer, nullable=False, server_default=text("'0'"))
    color = Column(String(6, u'utf8_bin'), nullable=False, server_default=text("'000000'"))
    label = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))

    sysmaps_element = relationship(u'SysmapsElement', primaryjoin='SysmapsLink.selementid1 == SysmapsElement.selementid')
    sysmaps_element1 = relationship(u'SysmapsElement', primaryjoin='SysmapsLink.selementid2 == SysmapsElement.selementid')
    sysmap = relationship(u'Sysmap')


class Timeperiod(Base):
    __tablename__ = 'timeperiods'

    timeperiodid = Column(BigInteger, primary_key=True)
    timeperiod_type = Column(Integer, nullable=False, server_default=text("'0'"))
    every = Column(Integer, nullable=False, server_default=text("'1'"))
    month = Column(Integer, nullable=False, server_default=text("'0'"))
    dayofweek = Column(Integer, nullable=False, server_default=text("'0'"))
    day = Column(Integer, nullable=False, server_default=text("'0'"))
    start_time = Column(Integer, nullable=False, server_default=text("'0'"))
    period = Column(Integer, nullable=False, server_default=text("'0'"))
    start_date = Column(Integer, nullable=False, server_default=text("'0'"))


class Trend(Base):
    __tablename__ = 'trends'

    itemid = Column(BigInteger, primary_key=True, nullable=False)
    clock = Column(Integer, primary_key=True, nullable=False, server_default=text("'0'"))
    num = Column(Integer, nullable=False, server_default=text("'0'"))
    value_min = Column(Float(16, True), nullable=False, server_default=text("'0.0000'"))
    value_avg = Column(Float(16, True), nullable=False, server_default=text("'0.0000'"))
    value_max = Column(Float(16, True), nullable=False, server_default=text("'0.0000'"))


class TrendsUint(Base):
    __tablename__ = 'trends_uint'

    itemid = Column(BigInteger, primary_key=True, nullable=False)
    clock = Column(Integer, primary_key=True, nullable=False, server_default=text("'0'"))
    num = Column(Integer, nullable=False, server_default=text("'0'"))
    value_min = Column(BigInteger, nullable=False, server_default=text("'0'"))
    value_avg = Column(BigInteger, nullable=False, server_default=text("'0'"))
    value_max = Column(BigInteger, nullable=False, server_default=text("'0'"))


class TriggerDepend(Base):
    __tablename__ = 'trigger_depends'
    __table_args__ = (
        Index('trigger_depends_1', 'triggerid_down', 'triggerid_up', unique=True),
    )

    triggerdepid = Column(BigInteger, primary_key=True)
    triggerid_down = Column(ForeignKey(u'triggers.triggerid', ondelete=u'CASCADE'), nullable=False)
    triggerid_up = Column(ForeignKey(u'triggers.triggerid', ondelete=u'CASCADE'), nullable=False, index=True)

    trigger = relationship(u'Trigger', primaryjoin='TriggerDepend.triggerid_down == Trigger.triggerid')
    trigger1 = relationship(u'Trigger', primaryjoin='TriggerDepend.triggerid_up == Trigger.triggerid')


t_trigger_discovery = Table(
    'trigger_discovery', metadata,
    Column('triggerid', ForeignKey(u'triggers.triggerid', ondelete=u'CASCADE'), primary_key=True),
    Column('parent_triggerid', ForeignKey(u'triggers.triggerid'), nullable=False, index=True)
)


class Trigger(Base):
    __tablename__ = 'triggers'
    __table_args__ = (
        Index('triggers_2', 'value', 'lastchange'),
    )

    triggerid = Column(BigInteger, primary_key=True)
    expression = Column(String(2048, u'utf8_bin'), nullable=False, server_default=text("''"))
    description = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    url = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    status = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    value = Column(Integer, nullable=False, server_default=text("'0'"))
    priority = Column(Integer, nullable=False, server_default=text("'0'"))
    lastchange = Column(Integer, nullable=False, server_default=text("'0'"))
    comments = Column(Text(collation=u'utf8_bin'), nullable=False)
    error = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("''"))
    templateid = Column(ForeignKey(u'triggers.triggerid', ondelete=u'CASCADE'), index=True)
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    state = Column(Integer, nullable=False, server_default=text("'0'"))
    flags = Column(Integer, nullable=False, server_default=text("'0'"))

    parent = relationship(u'Trigger', remote_side=[triggerid])
    parents = relationship(
        u'Trigger',
        secondary='trigger_discovery',
        primaryjoin=u'Trigger.triggerid == trigger_discovery.c.parent_triggerid',
        secondaryjoin=u'Trigger.triggerid == trigger_discovery.c.triggerid'
    )


class User(Base):
    __tablename__ = 'users'

    userid = Column(BigInteger, primary_key=True)
    alias = Column(String(100, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    name = Column(String(100, u'utf8_bin'), nullable=False, server_default=text("''"))
    surname = Column(String(100, u'utf8_bin'), nullable=False, server_default=text("''"))
    passwd = Column(String(32, u'utf8_bin'), nullable=False, server_default=text("''"))
    url = Column(String(255, u'utf8_bin'), nullable=False, server_default=text("''"))
    autologin = Column(Integer, nullable=False, server_default=text("'0'"))
    autologout = Column(Integer, nullable=False, server_default=text("'900'"))
    lang = Column(String(5, u'utf8_bin'), nullable=False, server_default=text("'en_GB'"))
    refresh = Column(Integer, nullable=False, server_default=text("'30'"))
    type = Column(Integer, nullable=False, server_default=text("'1'"))
    theme = Column(String(128, u'utf8_bin'), nullable=False, server_default=text("'default'"))
    attempt_failed = Column(Integer, nullable=False, server_default=text("'0'"))
    attempt_ip = Column(String(39, u'utf8_bin'), nullable=False, server_default=text("''"))
    attempt_clock = Column(Integer, nullable=False, server_default=text("'0'"))
    rows_per_page = Column(Integer, nullable=False, server_default=text("'50'"))


class UsersGroup(Base):
    __tablename__ = 'users_groups'
    __table_args__ = (
        Index('users_groups_1', 'usrgrpid', 'userid', unique=True),
    )

    id = Column(BigInteger, primary_key=True)
    usrgrpid = Column(ForeignKey(u'usrgrp.usrgrpid', ondelete=u'CASCADE'), nullable=False)
    userid = Column(ForeignKey(u'users.userid', ondelete=u'CASCADE'), nullable=False, index=True)

    user = relationship(u'User')
    usrgrp = relationship(u'Usrgrp')


class Usrgrp(Base):
    __tablename__ = 'usrgrp'

    usrgrpid = Column(BigInteger, primary_key=True)
    name = Column(String(64, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))
    gui_access = Column(Integer, nullable=False, server_default=text("'0'"))
    users_status = Column(Integer, nullable=False, server_default=text("'0'"))
    debug_mode = Column(Integer, nullable=False, server_default=text("'0'"))


class Valuemap(Base):
    __tablename__ = 'valuemaps'

    valuemapid = Column(BigInteger, primary_key=True)
    name = Column(String(64, u'utf8_bin'), nullable=False, unique=True, server_default=text("''"))


class ScmDailyServerUsage(Base):
    __tablename__ = 'scm_daily_server_usage'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    ServerTotalCount = Column(Integer)
    AssignedServerCount = Column(Integer, nullable=False)
    ServerNotInUSeCount = Column(Integer)
    AssignedServerInUseCount = Column(Integer)
    UsedRatio = Column(Float(asdecimal=True))
    AssignedRatio = Column(Float(asdecimal=True))


class ScmDailyServerUsageSeparate(Base):
    __tablename__ = 'scm_daily_server_usage_separate'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    ServerTotalCount = Column(Integer)
    region = Column(String(4, u'utf8_bin'), nullable=False, index=True)
    AssignedServerCount = Column(Integer, nullable=False)
    ServerNotInUSeCount = Column(Integer)
    UsedRatio = Column(Float(asdecimal=True))
    AssignedServerInUseCount = Column(Integer)
    AssignedRatio = Column(Float(asdecimal=True))

class ScmDailyServerWsUsageSeparate(Base):
    __tablename__ = 'scm_daily_server_ws_usage_separate'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    ServerTotalCount = Column(Integer)
    region = Column(String(4, u'utf8_bin'), nullable=False, index=True)
    AssignedServerCount = Column(Integer, nullable=False)
    ServerNotInUSeCount = Column(Integer)
    UsedRatio = Column(Float(asdecimal=True))

