import os
import sys
import urllib2

from datetime import date, datetime

#TODO: replace the following definitions with values from the Setting table or from the .ini file
from properties import (
    PROJECT_TITLE,
    FINAL_ID,
    FINAL_DEADLINE,
    ADMINS,
    GROUP_IDS 
    )

import webhelpers.paginate

from pyramid.response import Response

from pyramid.view import (
    view_config, 
    forbidden_view_config, 
    notfound_view_config
    )
from pyramid.renderers import render
from pyramid.url import route_url

from pyramid.security import (
    remember, 
    forget
    )

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound
    )

import formencode
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from sqlalchemy.schema import MetaData
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.serializer import (
    dumps as dump_table,
    loads as load_table
    )

from .models import (
    DBSession,
    Setting,
    Player,
    Rank,
    Category,
    Team,
    TeamGroup,
    Match,
    Final,
    Tip
    )

import scoring


# determine the local IP address to access this game
remote_server = Setting.get('result_server')
RESULTSERVER = remote_server.d_value if remote_server else 'euro2016.rolotec.ch'
RESULTPAGE = 'http://%s/results' % RESULTSERVER
local_host = 'localhost'
local_port = 8080   #TODO: extract port number from the server settings
try:
    from socket import create_connection
    s = create_connection((RESULTSERVER, 80))
    local_host = s.getsockname()[0]
    s.close()
except:
	pass
GAME_URL = 'http://%s:%d' % (local_host, local_port)


def items_per_page(request):
    """ Determine the pagination unit. This unit is determined
    as follows (in decreasing precedence):
    - from the request parameter 'items_per_page'
    - from the Setting table's entry named 'items_per_page'
    If none of the above matches or cannot be converted to
    an integer the default of 10 is returned.
    @return Number of items per page, default 10.
    """
    try:
        # expect exception, if param is missing or has a non-numeric value
       return int(request.params['items_per_page'])
    except: 
        try:
            setting = Setting.get('items_per_page')
            return int(setting.d_value)
        except:
            pass
    else:
        pass
    return 10

def get_int_param(request, param, default=None):
    """ @return Numerical value of named parameter. """
    try:
        return int(request.params[param])
    except:
        return default

def game_over():
    return datetime.now() >= datetime(2016,7,11)

def login_form_view(request):
    return render('templates/login.pt',
                  { 'loggedin': request.authenticated_userid },
                  request)

def navigation_view(request):
    return render('templates/navigation.pt',
                  { 'categories': sorted(Player.get_units()),
                    'game_over': game_over(),
                    'is_admin': request.authenticated_userid in ADMINS,
                    'viewer_username': request.authenticated_userid,
                    'login_form': login_form_view(request) },
                  request) if 'nonav' not in request.params else None

@forbidden_view_config()
def forbidden(request):
    return Response(body=render('templates/forbidden.pt',
                                { 'project': PROJECT_TITLE,
                                  'navigation': navigation_view(request) },
                                request));

@notfound_view_config()
def notfound(request):
    return Response(body=render('templates/notfound.pt',
                                { 'project': PROJECT_TITLE,
                                  'detail': request.exception.detail if request.exception else "no details",
                                  'navigation': navigation_view(request) },
                                request),
                    status='404 Not Found');

@view_config(permission='view', route_name='home', renderer='templates/main.pt')
def view_game(request):
    return { 'project': PROJECT_TITLE,
             'game_url': GAME_URL,
             'final_deadline': FINAL_DEADLINE,
             'game_over': game_over(),
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='about', renderer='templates/about.pt')
def about_view(request):
    return { 'project': PROJECT_TITLE,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='help', renderer='templates/help.pt')
def help_view(request):
    return { 'project': PROJECT_TITLE,
             'contact': Setting.get('admin_mail').d_value,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='results', renderer='json')
def results(request):
    """ Generate a list of scores for all played matches and the stage 2 team names. """
    matches = {}
    for match in Match.get_stage2():
        matches[match.d_id] = { "team1": match.d_team1, "team2": match.d_team2 }
    scores = {}
    for match in Match.get_played():
        scores[match.d_id] = { "score1": match.d_score1, "score2": match.d_score2 }
    return { 'matches': matches,
             'scores': scores }

@view_config(permission='view', route_name='scoring', renderer='templates/scoring.pt')
def scoring_view(request):
    return { 'project': PROJECT_TITLE,
             'num_matches': DBSession.query(Match).count(),
             'scoring': scoring.BET_POINTS,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='score_table', renderer='templates/score_table.pt')
def score_table(request):
    match_scores = [(score1, score2) for score1 in range(0, 6) for score2 in range(score1, 6)]
    matches = [Match(0, datetime.now(), 'team1', 'team2', score1, score2) for (score1, score2) in match_scores]
    tip_scores = [(score1, score2) for score1 in range(0, 6) for score2 in range(0, 6)]
    tips = [Tip('none', 0, score1, score2) for (score1, score2) in tip_scores]
    match_tips = [scoring.MatchTip(match, tip) for match in matches for tip in tips]
    return { 'match_tips': match_tips,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='categories', renderer='templates/categories.pt')
def view_categories(request):
    return { 'project': PROJECT_TITLE,
             'categories': Category.get_all(),
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='settings', renderer='templates/settings.pt')
def view_settings(request):
    return { 'project': PROJECT_TITLE,
             'settings': Setting.get_all(),
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='too_late', renderer='templates/too_late.pt')
def too_late(request):
    return { 'final_deadline': FINAL_DEADLINE,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }


# ----- Player views -----

class RegistrationSchema(formencode.Schema):
    allow_extra_fields = True
    alias = formencode.validators.String(not_empty=True, max=30)
    name = formencode.validators.String(not_empty=True)
    mail = formencode.validators.Email(resolve_domain=False, not_empty=True)
    #category = formencode.validators.OneOf(categories, hideList=True)
    initial_password = formencode.validators.String(not_empty=True, min=5)
    confirm_password = formencode.validators.String(not_empty=True, min=5)
    chained_validators = [
        formencode.validators.FieldsMatch('initial_password', 'confirm_password')
        #TODO: uniqueUsername(alias)
    ]

@view_config(permission='view', route_name='register', renderer='templates/register.pt')
def register(request):
    form = Form(request, schema=RegistrationSchema)
    if 'form.submitted' in request.POST and form.validate():
        alias = form.data['alias']
        if (Player.exists(alias)):
            request.session.flash(u'Alias "%(alias)s" is already used, please choose another one.' % form.data)
        else:
            player = Player(alias=alias,
                            password=form.data['initial_password'],
                            name=form.data['name'],
                            mail=form.data['mail'],
                            unit=form.data['category'])
            DBSession.add(player)
            headers = remember(request, alias)
            return HTTPFound(location=route_url('home', request), headers=headers)
    return { 'form': FormRenderer(form),
             'categories': Category.option_list(),
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='login')
def login(request):
    main_view = route_url('home', request)
    came_from = request.params.get('came_from', main_view)
    if 'form.submitted' in request.POST:
        login = request.POST['alias']
        password = request.POST['password']
        if Player.check_password(login, password):
            request.session.flash(u'Logged in successfully.')
            return HTTPFound(location=came_from, headers=remember(request, login))
        else:
            request.session.flash(u'Failed to login.')
    return HTTPFound(location=came_from)

@view_config(permission='post', route_name='logout')
def logout(request):
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    return HTTPFound(location=route_url('home', request), headers=forget(request))

@view_config(permission='view', route_name='view_players', renderer='templates/players.pt')
def view_players(request):
    ranking = Player.ranking()
    if not ranking:
        raise HTTPNotFound('no players yet')
    # Calculate every player's rank. Only the first player of each
    # rank gets a rank number, for all others it is set to None.
    rank = 1
    points = None
    for player in ranking:
        if points is None or player.d_points != points:
            player.rank = rank
            points = player.d_points
        rank += 1
    #for player in ranking:
    #    print'player %s with %d points = rank %s' % (player.d_alias, player.d_points, str(player.rank))
    url = webhelpers.paginate.PageURL_WebOb(request)
    page = get_int_param(request, param='page', default=1)
    players = webhelpers.paginate.Page(ranking,
                                       page=page,
                                       url=url,
                                       items_per_page=items_per_page(request))
    return { 'players': players,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

@view_config(permission='view', route_name='view_group_players', renderer='templates/group_players.pt')
def view_group_players(request):
    category_id = request.matchdict['category']
    players = Player.get_by_unit(category_id)
    if not players:
       raise HTTPNotFound('no players in category %s' % category_id)
    page = get_int_param(request, param='page', default=1)
    url = webhelpers.paginate.PageURL_WebOb(request)
    players = webhelpers.paginate.Page(players,
                                       page=page,
                                       url=url,
                                       items_per_page=items_per_page(request))
    category = Category.get(category_id)
    category_name = category.d_name if category else category_id
    return { 'category': category_id,
             'category_name': category_name,
             'players': players,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

@view_config(permission='view', route_name='view_rank_players', renderer='templates/rank_players.pt')
def view_rank_players(request):
    points = request.matchdict['points']
    players = Player.get_by_rank(points)
    if not players:
       raise HTTPNotFound('no players with %s points' % points)
    page = get_int_param(request, param='page', default=1)
    url = webhelpers.paginate.PageURL_WebOb(request)
    players = webhelpers.paginate.Page(players,
                                       page=page,
                                       url=url,
                                       items_per_page=items_per_page(request))
    return { 'points': points,
             'players': players,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

@view_config(permission='view', route_name='view_player_groups', renderer='templates/player_groups.pt')
def view_player_groups(request):
    groups = Player.get_groups()
    if not groups:
        raise HTTPNotFound('no player groups yet')
    # sort categories by descending average number of points
    ranking = []
    rank = 1
    points = None
    for group in sorted(groups, lambda g1,g2: scoring.sign((float(g1[3]) / g1[2]) - (float(g2[3]) / g2[2])), reverse=True):
        category = Category(group[1], Category.get(group[1]).d_name)
        category.players = int(group[2])
        category.points = float(group[3]) / category.players
        if points is None or category.points != points:
            category.rank = rank
            points = category.points
        ranking.append(category)
        rank += 1
    page = get_int_param(request, param='page', default=1)
    url = webhelpers.paginate.PageURL_WebOb(request)
    categories = webhelpers.paginate.Page(ranking,
                                          page=page,
                                          url=url,
                                          items_per_page=items_per_page(request))
    return { 'categories': categories,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

@view_config(permission='view', route_name='view_ranking', renderer='templates/ranking.pt')
def view_ranking(request):
    ranks = Rank.get_all()
    if not ranks:
        raise HTTPNotFound('no ranking yet')
    url = webhelpers.paginate.PageURL_WebOb(request)
    page = get_int_param(request, param='page', default=1)
    ranks = webhelpers.paginate.Page(ranks,
                                     page=page,
                                     url=url,
                                     items_per_page=items_per_page(request))
    player = Player.get_by_username(request.authenticated_userid)
    player_rank = Rank.get_position(player.d_points) if player else None
    return { 'ranks': ranks,
             'player_rank': player_rank.d_position if player_rank else None,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

class PlayerInfo(formencode.Schema):
    allow_extra_fields = True
    name = formencode.validators.String(not_empty=True)
    mail = formencode.validators.Email(resolve_domain=False, not_empty=True)

@view_config(permission='post', route_name='player_info', renderer='templates/player_info.pt')
def view_player_info(request):
    player = Player.get_by_username(request.authenticated_userid)
    form = Form(request, schema=PlayerInfo, obj=player)
    if 'form.submitted' in request.POST and form.validate():
        player.d_name = form.data['name']
        player.d_mail = form.data['mail']
        player.d_unit = form.data['category']
        request.session.flash(u'Player information has been updated.')
    player_rank = Rank.get_position(player.d_points) if player else None
    return { 'form': FormRenderer(form),
             'player': player,
             'player_rank': player_rank.d_position if player_rank else None,
             'viewer_username': request.authenticated_userid,
             'categories': Category.option_list(),
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }


# ----- Team/Group views -----

@view_config(permission='view', route_name='view_teams', renderer='templates/teams.pt')
def view_teams(request):
    """ Alphabetical team list. """
    return { 'teams': Team.get_all(),
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_team_groups', renderer='templates/team_groups.pt')
def view_team_groups(request):
    """ Show all teams of all groups. """
    groups = [TeamGroup(group_id, Team.get_by_group(group_id)) for group_id in GROUP_IDS]
    return { 'groups': groups,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

@view_config(permission='view', route_name='view_group_teams', renderer='templates/group_teams.pt')
def view_group_teams(request):
    """ Show the teams of a single group. """
    player = request.authenticated_userid
    group_id = request.matchdict['group']
    if group_id not in GROUP_IDS:
        raise HTTPNotFound('invalid group id: %s' % group_id)
    group = TeamGroup(group_id, Team.get_by_group(group_id))
    matches = Match.get_by_group(group_id).all()
    view = match_view(request, player, matches, 'unused title', group_id)
    view.update({ 'group': group })
    return view


# ----- Match views -----

def match_view(request, player, matches, title, group_id=None):
    for match in matches:
        if player:
            if match.d_id == FINAL_ID:
                final_tip = Final.get_player_tip(player)
                match.tip = Tip(player, FINAL_ID, final_tip.d_score1, final_tip.d_score2) if final_tip else None
            else:
                match.tip = Tip.get_player_tip(player, match.d_id)
        else:
            match.tip = None
    return { 'now': datetime.now(),
             'title': title,
             'matches': matches,
             'group_id': group_id,
             'final_id': FINAL_ID,
             'final_deadline': FINAL_DEADLINE,
             'viewer_username': player,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

@view_config(permission='view', route_name='view_matches', renderer='templates/matches.pt', http_cache=0)
def view_matches(request):
    player = request.authenticated_userid
    matches = Match.get_all()
    return match_view(request, player, matches, 'Match schedule')

@view_config(permission='view', route_name='view_upcoming_matches', renderer='templates/matches.pt', http_cache=0)
def view_upcoming_matches(request):
    player = request.authenticated_userid
    num = request.matchdict['num']
    matches = Match.get_upcoming(date.today(), num)
    return match_view(request, player, matches, 'Upcoming matches')

@view_config(permission='view', route_name='view_group_matches', renderer='templates/matches.pt', http_cache=0)
def view_group_matches(request):
    player = request.authenticated_userid
    group_id = request.matchdict['group']
    matches = Match.get_by_group(group_id).all()
    return match_view(request, player, matches, 'Group %s matches' % group_id, group_id)

@view_config(permission='view', route_name='view_stage2_matches', renderer='templates/matches.pt', http_cache=0)
def view_stage2_matches(request):
    player = request.authenticated_userid
    matches = Match.get_stage2().all()
    return match_view(request, player, matches, 'Stage 2 matches')


# ----- Tip views -----

class MatchBetSchema(formencode.Schema):
    allow_extra_fields = True
    d_score1 = formencode.validators.Int(min=0, max=100, not_empty=True)
    d_score2 = formencode.validators.Int(min=0, max=100, not_empty=True)

@view_config(permission='post', route_name='match_bet', renderer='templates/match_bet.pt')
def match_bet(request):
    player_id = request.authenticated_userid
    match_id = request.matchdict['match']
    match = Match.get_by_id(match_id)
    if match.d_begin < datetime.now():
        return HTTPFound(location=route_url('too_late', request))

    tip = Tip.get_player_tip(player_id, match_id)

    form = Form(request, schema=MatchBetSchema, obj=tip)
    if 'form.submitted' in request.POST and form.validate():
        if not tip:
            tip = Tip(player=player_id, match=match_id)
            DBSession.add(tip)
        tip.d_score1 = form.data['d_score1']
        tip.d_score2 = form.data['d_score2']
        return HTTPFound(location=route_url('view_match_tips', request, match=match_id))

    return { 'match': match,
             'tip': tip,
             'form': FormRenderer(form),
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_match_tips', renderer='templates/match_tips.pt', http_cache=0)
def view_match_tips(request):
    match_id = request.matchdict['match']
    match = Match.get_by_id(match_id)
    match_tips = [scoring.MatchTip(match, tip) for tip in Tip.get_match_tips(match_id)]
    page = get_int_param(request, param='page', default=1)
    url = webhelpers.paginate.PageURL_WebOb(request)
    tips = webhelpers.paginate.Page(match_tips,
                                    page=page,
                                    url=url,
                                    items_per_page=items_per_page(request))
    return { 'match': match,
             'tips': tips,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

@view_config(permission='view', route_name='view_player_tips', renderer='templates/player_tips.pt', http_cache=0)
def view_player_tips(request):
    player_id = request.matchdict['player']
    player = Player.get_by_username(player_id)
    tips = []
    for tip in Tip.get_player_tips(player_id):
        match = Match.get_by_id(tip.d_match)
        tips.append(scoring.MatchTip(match, tip))
    final = Match.get_final()
    final_tip = Final.get_player_tip(player_id)
    if final and final_tip:
        tips.append(scoring.FinalTip(final, final_tip))
    return { 'player': player,
             'tips': tips,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }


# ----- Final views -----

class FinalBetSchema(formencode.Schema):
    allow_extra_fields = True
    d_team1 = formencode.validators.String(not_empty=True)
    d_team2 = formencode.validators.String(not_empty=True)
    d_score1 = formencode.validators.Int(min=0, not_empty=True)
    d_score2 = formencode.validators.Int(min=0, not_empty=True)

@view_config(permission='post', route_name='final_bet', renderer='templates/final_bet.pt')
def final_bet(request):
    player = request.authenticated_userid
    final_tip = Final.get_player_tip(player)
    if final_tip:
        request.session.flash(u'You already entered a final tip.')
        return HTTPFound(location=route_url('view_final_tip', request, player=player))

    final_tip = Final(player)

    form = Form(request, schema=FinalBetSchema, obj=final_tip)
    if 'form.submitted' in request.POST and form.validate():
        # verify, that the tip was entered on time
        if FINAL_DEADLINE < datetime.now():
            return HTTPFound(location=route_url('too_late', request))
        final_tip.d_team1 = form.data['d_team1']
        final_tip.d_team2 = form.data['d_team2']
        final_tip.d_score1 = form.data['d_score1']
        final_tip.d_score2 = form.data['d_score2']
        DBSession.add(final_tip)
        return HTTPFound(location=route_url('view_final_tip', request, player=player))

    teams = [(team.d_id,team.d_name) for team in Team.get_all()]

    return { 'tip': final_tip,
             'form': FormRenderer(form),
             'teams': teams,
             'navigation': navigation_view(request) }

@view_config(permission='view', route_name='view_final_tips', renderer='templates/final_tips.pt', http_cache=0)
def view_final_tips(request):
    final = Match.get_final()
    tips = [scoring.FinalTip(final, tip) for tip in Final.get_all()]
    return { 'final': final,
             'tips': tips,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

@view_config(permission='view', route_name='view_final_tip', renderer='templates/final_tip.pt', http_cache=0)
def view_final_tip(request):
    player = request.matchdict['player']
    tip = Final.get_player_tip(player)
    return { 'tip': tip,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }


# ----- Admin stuff -----

@view_config(permission='admin', route_name='tips', renderer='templates/tips.pt', http_cache=0)
def view_tips(request):
    return { 'tips': Tip.get_all(),
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }

@view_config(permission='admin', route_name='update_local')
def update_local(request):
    scoring.refresh_points()
    return HTTPFound(location=route_url('view_players', request))

@view_config(permission='view', route_name='update_remote')
def update_remote(request):
    try:
        scoring.apply_results(urllib2.urlopen(RESULTPAGE).read())
        return HTTPFound(location=route_url('view_players', request))
    except:
        raise HTTPNotFound('location <%s> is inaccessible.' % RESULTPAGE)

@view_config(permission='admin', route_name='mailing', renderer='templates/mailing.pt')
def mailing(request):
    groups = Player.get_groups()
    if not groups:
        raise HTTPNotFound('no player groups yet')
    everybody = []
    categories = {}
    for group in sorted(groups):
        players = Player.get_by_unit(group.d_unit)
        addrs = [player.d_mail for player in players]
        categories[group.d_unit] = ";".join(addrs)
        everybody.extend(addrs)
    return { 'everybody': ";".join(everybody),
             'categories': categories,
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request),
             'nonav': 'nonav' in request.params }

@view_config(permission='admin', route_name='unregister')
def unregister(request):
    alias = request.matchdict['alias']
    player = Player.get_by_username(alias)
    if player:
        DBSession.delete(player)
        request.session.flash(u'Player "%(alias)s" deleted.' % request.matchdict)
    else:
        request.session.flash(u'Player "%(alias)s" not found.' % request.matchdict)
    return HTTPFound(location=route_url('view_players', request))

@view_config(permission='admin', route_name='update_category')
def update_category(request):
    try:
        name = request.matchdict['name']
        value = request.matchdict['value']
        category = Category.get(name)
        if value == 'DELETE':
            # delete category unless it is used by some players
            if category:
                players = Player.get_by_unit(name)
                if players and len(players.all()) > 0:
                    request.session.flash(u'Category "%(name)s" cannot be deleted.' % request.matchdict)
                else:
                    DBSession.delete(category)
                    request.session.flash(u'Deleted category "%(name)s".' % request.matchdict)
            else:
                request.session.flash(u'Category "%(name)s" does not exist.' % request.matchdict)
        else:
            # update/create category
            if category:
                category.d_name = value
                request.session.flash(u'Updated category "%(name)s".' % request.matchdict)
            else:
                category = Category(name, value)
                DBSession.add(category)
                request.session.flash(u'Created category "%(name)s".' % request.matchdict)
    except:
        request.session.flash(u'Failed to update or create category "%(name)s".' % request.matchdict)
    return HTTPFound(location=route_url('categories', request))

@view_config(permission='admin', route_name='update_match')
def update_match(request):
    try:
        match = Match.get_by_id(request.matchdict['id'])
        if match:
            if match.d_begin < STAGE2_DEADLINE: 
                request.session.flash(u'Cannot update group stage matches.')
            else:
                match.d_team1 = request.matchdict['team1']
                match.d_team2 = request.matchdict['team2']
        else:
            request.session.flash(u'Invalid match id: %(id)s.' % request.matchdict)
        return HTTPFound(location=route_url('view_matches', request))
    except:
        request.session.flash(u'Updating match teams failed.')
        return HTTPFound(location=route_url('view_matches', request))

@view_config(permission='admin', route_name='update_score')
def update_score(request):
    try:
        match = Match.get_by_id(request.matchdict['id'])
        if match:
            score1 = int(request.matchdict['score1'])
            match.d_score1 = score1 if score1 >= 0 else None
            score2 = int(request.matchdict['score2'])
            match.d_score2 = score2 if score2 >= 0 else None
        else:
            request.session.flash(u'Invalid match id: %(id)s.' % request.matchdict)
        return HTTPFound(location=route_url('view_matches', request))
    except:
        request.session.flash(u'Updating score and points failed.')
        return HTTPFound(location=route_url('view_matches', request))

@view_config(permission='admin', route_name='update_setting')
def update_setting(request):
    try:
        name = request.matchdict['name']
        value = request.matchdict['value']
        setting = Setting.get(name)
        if value == 'DELETE':
            if setting:
                if setting.d_name.startswith('scoring_'):
                    request.session.flash(u'Setting "%(name)s" cannot be deleted.' % request.matchdict)
                else:
                    DBSession.delete(setting)
                    request.session.flash(u'Deleted setting "%(name)s".' % request.matchdict)
            else:
                request.session.flash(u'Setting "%(name)s" does not exist.' % request.matchdict)
        else:
            if setting:
                setting.d_value = value
                request.session.flash(u'Updated setting "%(name)s".' % request.matchdict)
            else:
                setting = Setting(name, value)
                DBSession.add(setting)
                request.session.flash(u'Created setting "%(name)s".' % request.matchdict)
            if setting.d_name.startswith('scoring_'):
                scoring.reload_betpoints()
    except:
        request.session.flash(u'Failed to update or create setting "%(name)s".' % request.matchdict)
    return HTTPFound(location=route_url('settings', request))

@view_config(permission='admin', route_name='db_backup')
def db_backup(request):
    table = request.matchdict['table']
    if table == 'categories':
        data = dump_table(DBSession.query(Category).all())
    elif table == 'settings':
        data = dump_table(DBSession.query(Setting).all())
    elif table == 'players':
        data = dump_table(DBSession.query(Player).all())
    elif table == 'matches':
        data = dump_table(DBSession.query(Match).all())
    elif table == 'teams':
        data = dump_table(DBSession.query(Team).all())
    elif table == 'tips':
        data = dump_table(DBSession.query(Tip).all())
    elif table == 'final':
        data = dump_table(DBSession.query(Final).all())
    else:
        raise HTTPNotFound('unknown table: %(table)s' % request.matchdict)
    response = Response(headers={ 'mime-type': 'application/octet-stream' }, body=data)
    response.content_length = len(data)
    response.content_disposition = 'attachment;filename="%(table)s.dat"' % request.matchdict
    return response

@view_config(permission='admin', route_name='db_restore', renderer='templates/restore.pt')
def db_restore(request):
    if 'form.submitted' in request.POST:
        data = request.POST.get('data')
        if data is not None:
            data = data.file.read()
            #print 'data(content, %d bytes): %s' % (len(data), data)
            if len(data) > 0:
                try:
                    query = load_table(data, scoped_session=DBSession)
                    for obj in query:
                        DBSession.merge(obj)
                    request.session.flash(u'Restore succeeded.')
                    return HTTPFound(location=route_url('home', request))
                except:
                    request.session.flash(u'Not a valid backup file.')
            else:
                request.session.flash(u'Empty backup file.')
        else:
            request.session.flash(u'Please select a file.')
    form = Form(request)
    return { 'form': FormRenderer(form),
             'navigation': navigation_view(request) }

@view_config(permission='admin', route_name='system_info', renderer='templates/sysinfo.pt')
def system_info(request):
    sysinfo = {
        'os.name': os.name,
        'sys.platform': sys.platform,
        'sys.maxint': sys.maxint,
        'sys.maxsize': sys.maxsize
    }
    with open('/proc/version') as f:
        sysinfo['os.version'] = f.read().strip()
    with open('/proc/cpuinfo') as f:
        for line in f:
            info = line.strip().split(': ')
            #print "cpuinfo: %s (%d)" % (info, len(info))
            if len(info) > 0 and info[0].strip() != '':
                key = 'cpu.%s' % info[0].strip() 
                value = info[1].strip() if len(info) > 1 else '---'
                sysinfo[key] = value
    with open('/proc/meminfo') as f:
        for line in f:
            info = line.strip().split(': ')
            #print "meminfo: %s (%d)" % (info, len(info))
            if len(info) > 0 and info[0].strip() != '':
                key = 'mem.%s' % info[0].strip() 
                value = info[1].strip() if len(info) > 1 else '---'
                sysinfo[key] = value
    for key,value in request.registry.settings.iteritems():
        sysinfo['ini.%s' % key] = value
    return { 'sysinfo': sorted(sysinfo.items()),
             'viewer_username': request.authenticated_userid,
             'navigation': navigation_view(request) }
