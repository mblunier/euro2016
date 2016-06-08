# -*- coding: utf-8 -*-

import os
import sys
import transaction

from datetime import datetime

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Setting,
    Team,
    Match,
    Final,
    Player,
    Category,
    Base
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    # register the 'admin' user
    with transaction.manager:
        DBSession.add(Player(alias="admin", password="None", name="Admin", mail="markus.blunier@six-group.com", unit="Administration"))

    # player categories (org. units)
    with transaction.manager:
        #DBSession.add(Category(alias="Admin",       name="Administration"))
        DBSession.add(Category(alias="DFI-FDMD",    name="Data Production / Quality Support MD"))
        DBSession.add(Category(alias="DFI-MMOC",    name="Marketing Communications"))
        DBSession.add(Category(alias="DFI-MPMI",    name="Public Interface Capabilities"))
        DBSession.add(Category(alias="DFI-MPMP",    name="Product Propositions"))
        DBSession.add(Category(alias="DFI-MPMV",    name="Value Added Services"))
        DBSession.add(Category(alias="DFS-ARG",     name="Accounting"))
        DBSession.add(Category(alias="DGI-AFD",     name="Product Delivery Appl. Engineering"))
        DBSession.add(Category(alias="DGI-AFDA",    name="Data Aggregation and Enrichment"))
        DBSession.add(Category(alias="DGI-AFDC",    name="Content Applications"))
        DBSession.add(Category(alias="DGI-AFDD",    name="Delivery Application"))
        DBSession.add(Category(alias="DGI-AFDF",    name="Product Eng. & QA"))
        DBSession.add(Category(alias="DGI-AFDN",    name="API Engineering"))
        DBSession.add(Category(alias="DGI-AFDS",    name="Services Framework"))
        DBSession.add(Category(alias="DGI-AFDW",    name="Web Applications"))
        DBSession.add(Category(alias="DGI-AFPD",    name="RefData & RefCalc"))
        DBSession.add(Category(alias="DGI-AO",      name="Card Mgmt & Online Systems"))
        DBSession.add(Category(alias="DGI-AOF",     name="Application Engineering Frontoffice"))
        DBSession.add(Category(alias="DGI-AOFA",    name="Frontoffice Acquiring"))
        DBSession.add(Category(alias="DGI-AOFI",    name="Frontoffice Issuing"))
        DBSession.add(Category(alias="DGI-AOFN",    name="Frontoffice Architecture"))
        DBSession.add(Category(alias="DGI-AOFP",    name="Platform DBA and Security"))
        DBSession.add(Category(alias="DGI-AOFS",    name="FO System Test Deployment and Support"))
        DBSession.add(Category(alias="DGI-AOFW",    name="Frontoffice Web Services"))
        DBSession.add(Category(alias="DGI-FE",      name="Engagement Management"))
        DBSession.add(Category(alias="DGI-OVS",     name="Operations & Support"))
        DBSession.add(Category(alias="DGI-PR",      name="Requirements and Solutions"))
        DBSession.add(Category(alias="DPS-SXAC",    name="Processing & Scheme Engineering"))
        DBSession.add(Category(alias="DPS-SXEB",    name="Terminal Engineering"))
        DBSession.add(Category(alias="DPS-SXS",     name="Solutions, Architecture & Chip"))
        DBSession.add(Category(alias="SGR-HDAI",    name="IT Apprentice"))

    # teams/groups
    with transaction.manager:
        DBSession.add(Team(id='ALB', name=u'Albania',      group='A'))
        DBSession.add(Team(id='FRA', name=u'France',       group='A'))
        DBSession.add(Team(id='ROU', name=u'Romania',      group='A'))
        DBSession.add(Team(id='SUI', name=u'Switzerland',  group='A'))

        DBSession.add(Team(id='ENG', name=u'England',      group='B'))
        DBSession.add(Team(id='RUS', name=u'Russia',       group='B'))
        DBSession.add(Team(id='SVK', name=u'Slovakia',     group='B'))
        DBSession.add(Team(id='WAL', name=u'Wales',        group='B'))

        DBSession.add(Team(id='GER', name=u'Germany',      group='C'))
        DBSession.add(Team(id='NIR', name=u'N. Ireland',   group='C'))
        DBSession.add(Team(id='POL', name=u'Poland',       group='C'))
        DBSession.add(Team(id='UKR', name=u'Ukraine',      group='C'))

        DBSession.add(Team(id='CRO', name=u'Croatia',      group='D'))
        DBSession.add(Team(id='CZE', name=u'Czech Rep.',   group='D'))
        DBSession.add(Team(id='ESP', name=u'Spain',        group='D'))
        DBSession.add(Team(id='TUR', name=u'Turkey',       group='D'))

        DBSession.add(Team(id='BEL', name=u'Belgium',      group='E'))
        DBSession.add(Team(id='ITA', name=u'Italy',        group='E'))
        DBSession.add(Team(id='IRL', name=u'Rep. Ireland', group='E'))
        DBSession.add(Team(id='SWE', name=u'Sweden',       group='E'))

        DBSession.add(Team(id='AUT', name=u'Austria',      group='F'))
        DBSession.add(Team(id='HUN', name=u'Hungary',      group='F'))
        DBSession.add(Team(id='ISL', name=u'Iceland',      group='F'))
        DBSession.add(Team(id='POR', name=u'Portugal',     group='F'))

    # tournament schedule
    with transaction.manager:
        # match day 1
        DBSession.add(Match(id= 1, begin=datetime(2016,6,10, 21,00), team1='FRA', team2='ROU'))
        DBSession.add(Match(id= 2, begin=datetime(2016,6,11, 15,00), team1='ALB', team2='SUI'))
        DBSession.add(Match(id= 3, begin=datetime(2016,6,11, 18,00), team1='WAL', team2='SVK'))
        DBSession.add(Match(id= 4, begin=datetime(2016,6,11, 21,00), team1='ENG', team2='RUS'))
        DBSession.add(Match(id= 5, begin=datetime(2016,6,12, 15,00), team1='TUR', team2='CRO'))
        DBSession.add(Match(id= 6, begin=datetime(2016,6,12, 18,00), team1='POL', team2='NIR'))
        DBSession.add(Match(id= 7, begin=datetime(2016,6,12, 21,00), team1='GER', team2='UKR'))
        DBSession.add(Match(id= 8, begin=datetime(2016,6,13, 15,00), team1='ESP', team2='CZE'))
        DBSession.add(Match(id= 9, begin=datetime(2016,6,13, 18,00), team1='IRL', team2='SWE'))
        DBSession.add(Match(id=10, begin=datetime(2016,6,13, 21,00), team1='BEL', team2='ITA'))
        DBSession.add(Match(id=11, begin=datetime(2016,6,14, 18,00), team1='AUT', team2='HUN'))
        DBSession.add(Match(id=12, begin=datetime(2016,6,14, 21,00), team1='POR', team2='ISL'))
        # match day 2
        DBSession.add(Match(id=13, begin=datetime(2016,6,15, 15,00), team1='RUS', team2='SVK'))
        DBSession.add(Match(id=14, begin=datetime(2016,6,15, 18,00), team1='ROU', team2='SUI'))
        DBSession.add(Match(id=15, begin=datetime(2016,6,15, 21,00), team1='FRA', team2='ALB'))
        DBSession.add(Match(id=16, begin=datetime(2016,6,16, 15,00), team1='ENG', team2='WAL'))
        DBSession.add(Match(id=17, begin=datetime(2016,6,16, 18,00), team1='UKR', team2='NIR'))
        DBSession.add(Match(id=18, begin=datetime(2016,6,16, 21,00), team1='GER', team2='POL'))
        DBSession.add(Match(id=19, begin=datetime(2016,6,17, 15,00), team1='ITA', team2='SWE'))
        DBSession.add(Match(id=20, begin=datetime(2016,6,17, 18,00), team1='CZE', team2='CRO'))
        DBSession.add(Match(id=21, begin=datetime(2016,6,17, 21,00), team1='ESP', team2='TUR'))
        DBSession.add(Match(id=22, begin=datetime(2016,6,18, 15,00), team1='BEL', team2='IRL'))
        DBSession.add(Match(id=23, begin=datetime(2016,6,18, 18,00), team1='ISL', team2='HUN'))
        DBSession.add(Match(id=24, begin=datetime(2016,6,18, 21,00), team1='POR', team2='AUT'))
        # match day 3
        DBSession.add(Match(id=25, begin=datetime(2016,6,19, 21,00), team1='SUI', team2='FRA'))
        DBSession.add(Match(id=26, begin=datetime(2016,6,19, 21,00), team1='ROU', team2='ALB'))
        DBSession.add(Match(id=27, begin=datetime(2016,6,20, 21,00), team1='SVK', team2='ENG'))
        DBSession.add(Match(id=28, begin=datetime(2016,6,20, 21,00), team1='RUS', team2='WAL'))
        DBSession.add(Match(id=29, begin=datetime(2016,6,21, 18,00), team1='NIR', team2='GER'))
        DBSession.add(Match(id=30, begin=datetime(2016,6,21, 18,00), team1='UKR', team2='POL'))
        DBSession.add(Match(id=31, begin=datetime(2016,6,21, 21,00), team1='CRO', team2='ESP'))
        DBSession.add(Match(id=32, begin=datetime(2016,6,21, 21,00), team1='CZE', team2='TUR'))
        DBSession.add(Match(id=33, begin=datetime(2016,6,22, 18,00), team1='ISL', team2='AUT'))
        DBSession.add(Match(id=34, begin=datetime(2016,6,22, 18,00), team1='HUN', team2='POR'))
        DBSession.add(Match(id=35, begin=datetime(2016,6,22, 21,00), team1='SWE', team2='BEL'))
        DBSession.add(Match(id=36, begin=datetime(2016,6,22, 21,00), team1='ITA', team2='IRL'))
        # round of 16
        DBSession.add(Match(id=37, begin=datetime(2016,6,25, 15,00), team1= '2A', team2= '2C'))
        DBSession.add(Match(id=38, begin=datetime(2016,6,25, 18,00), team1= '1B', team2='3ACD'))
        DBSession.add(Match(id=39, begin=datetime(2016,6,25, 21,00), team1= '1D', team2='3BEF'))
        DBSession.add(Match(id=40, begin=datetime(2016,6,26, 15,00), team1= '1A', team2='3CDE'))
        DBSession.add(Match(id=41, begin=datetime(2016,6,26, 18,00), team1= '1C', team2='3ABF'))
        DBSession.add(Match(id=42, begin=datetime(2016,6,26, 21,00), team1= '1F', team2= '2E'))
        DBSession.add(Match(id=43, begin=datetime(2016,6,27, 18,00), team1= '1E', team2= '2D'))
        DBSession.add(Match(id=44, begin=datetime(2016,6,27, 21,00), team1= '2B', team2= '2F'))
        # quarter finals
        DBSession.add(Match(id=45, begin=datetime(2016,6,30, 21,00), team1='W37', team2='W39'))
        DBSession.add(Match(id=46, begin=datetime(2016,7, 1, 21,00), team1='W38', team2='W42'))
        DBSession.add(Match(id=47, begin=datetime(2016,7, 2, 21,00), team1='W41', team2='W43'))
        DBSession.add(Match(id=48, begin=datetime(2016,7, 3, 21,00), team1='W40', team2='W44'))
        # semi finals
        DBSession.add(Match(id=49, begin=datetime(2016,7, 6, 21,00), team1='W45', team2='W46'))
        DBSession.add(Match(id=50, begin=datetime(2016,7, 7, 21,00), team1='W47', team2='W48'))
        # final
        DBSession.add(Match(id=51, begin=datetime(2016,7,10, 21,00), team1='W49', team2='W50'))

    with transaction.manager:
        DBSession.add(Setting(name="result_server",        value="euro2016.rolotec.ch"))
        DBSession.add(Setting(name="admin_alias",          value="admin"))
        DBSession.add(Setting(name="admin_mail",           value="mblunier@gmx.ch"))
        DBSession.add(Setting(name="scoring_exacthit",     value="5"))
        DBSession.add(Setting(name="scoring_outcome",      value="3"))
        DBSession.add(Setting(name="scoring_missed",       value="1"))
        DBSession.add(Setting(name="scoring_sumgoals",     value="3"))
        DBSession.add(Setting(name="scoring_goaldiff",     value="2"))
        DBSession.add(Setting(name="scoring_onescore",     value="1"))
        DBSession.add(Setting(name="scoring_onefinalist",  value="5"))
        DBSession.add(Setting(name="scoring_twofinalists", value="10"))
