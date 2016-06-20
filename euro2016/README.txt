Euro2016 README
===============

Getting Started
---------------

- Setup and activate a virtual Python environment (do this as a normal user!):
	$ mkdir betgame
	$ virtualenv --no-site-packages betgame
	$ cd betgame
	$ source bin/activate

- Upgrade the setuptools:
  	(betgame)$ pip install setuptools --upgrade

- Get a copy of the distributed game 'euro2016-x.y.tar.gz'.

- Install the game (this step must be repeated for every new release):
	(betgame)$ easy_install path/to/euro2016-x.y.tar.gz

- Edit the categories in 'betgame/lib/python2.7/site-packages/euro2016-x.y-py2.7.egg/euro2016/scripts/initialize_db.py'.
  Categories may also be adapted later by the administrator (see below).

- Extract the production.ini file from the archive and adapt it as desired
  (as port 80 is reserved for root the default port is 8080).

- Initialize database content:
	(betgame)$ initialize_euro2016_db production.ini

- Launch the service:
	(betgame)$ pserve production.ini

  In case the daemontools are available for the target platform there exist a
  few scripts to start, stop and control the game. Initially copy the file
  'scripts/run' to the directory $HOME/proc/svc/betgame. Then copy the
  'start', 'stop', 'stat' and 'restart' scripts to $HOME. Thereafter the game
  may be controlled by means of ~/(start|stop|stat|restart).

  The command to launch the service is then as follows:
	(betgame)$ ~/start betgame

- Open the URL http://<hostname_or_ip>:8080 (or whatever port number you
  have chosen) in your preferred web browser.

- In order to operate the game behind a proxy enable the virtual host config
  from 'euro2016.conf'. Afterwards the game can be accessed via the virtual
  hostname without explicit port number.


Administration
--------------
Some pages are restricted to the administrator(s) maintaining a betgame
instance. The "list" of administrator aliases is currently hard-coded in
'properties.py'.

Once everything is initialized most of the required steps can be automated.
This chapter describes the available functions (all URLs relative to the root URL):

  /backup/{table}
	Dumps the binary content of the indicated table. Available table
	names are: 'categories', 'settings', 'players', 'matches', 'teams',
	'tips' and 'final'. Their content should be saved as files to be
	available for restoring.

	The script 'backup-betgame.sh' is available to automate the backup of
	all relevant tables from a betgame instance. By default the data is
	retrieved from localhost:8080 but a different server (hostname or IP
	plus port number) may be specified.

  /category/{name}/{value}
	Creates or updates category {name}. When specifying 'DELETE' as {value}
	the corresponding category is deleted unless there exist players with
	this category. Any other {value} just updates or creates the category.

  /match/{id}/{team1}/{team2}
	Specifies the team mnemonics for the stage 2 match with id {id}. This
	is required after stage 1 and after every stage 2 match.

  /restore
	Displays a form to specify a data file with saved table contents.
	After submitting the form the file is uploaded and its content
	replaces all entries with matching keys.

  /score/{id}/{score1}/{score2}
	Specifies the score for the match with id {id}. This is required
	after every match. Using -1 for the scores deletes the score.

  /setting/{name}/{value}
	Creates or updates a setting (see below). Settings may be deleted by
	specifying 'DELETE' as {value}. Settings, whose name starts with
	'scoring_' cannot be deleted, however.

  /sysinfo
  	Shows information about the server where the game is running.

  /unregister/{alias}
	Deletes the player {alias} together with all related data from the DB.
	THIS CANNOT BE UNDONE!

  /update_local
	Updates all team & player points according to the locally stored match
	results.

  /update_remote
	Updates all team & player points according to the match results stored
	on the configured result server (default: 'euro2016.rolotec.ch'). Calling
	this function regularly or at least after every match suffices to keep 
	the local instance up to date.


Special views
-------------
The following views are not directly reachable via the links within the game:

  /infoscreen
	Displays a special view describing the access to the local game
	instance.

  /results
	Returns all present match scores and stage 2 teams in JSON format.

  /settings
	Shows the list of all defined settings and their values.

When adding '?nonav'  to any view the navigation and all embedded hyperlinks
are suppressed.


Settings
--------
Some aspects of the game are customizable via the Setting table. The following
keys are recognized:

  admin_alias (default: admin)
	The alias of the admin user. Note, that the admin user is excluded
	from the game and does not occur in any of the rankings.

  admin_mail (default: admin@rolotec.ch)
	The contact mail shown on the help page.

  result_server (default: euro2016.rolotec.ch)
	The name of the server providing match results. Any instance of the
	betgame where results are entered may be used.

  items_per_page
	The number of items shown on pages with pagination. The configured
	value may be overridden when specifying it as an URL parameter; e.g.
	<http://hostname/players?items_per_page=20>.

  scoring_exacthit (default: 5)
	The number of points for an exact hit.

  scoring_goaldiff (default: 2)
	The number of points for guessing the goal difference.

  scoring_missed (default: 1)
	The number of points for entering a bet. Only taken if neither an
	exact hit nor the outcome was guessed.

  scoring_onefinalist (default: 5)
	Number of points for guessing 1 finalist.

  scoring_onescore (default: 1)
	The number of points for guessing 1 score exactly. Not used for the
	default scoring algorithm.

  scoring_outcome (default: 3)
	The number of points for guessing the outcome (1/X/2) without hitting
	the exact result.

  scoring_sumgoals (default: 3)
	The number of points for guessing the goal difference.

  scoring_twofinalists (default: 10)
	Number of points for guessing both finalists.

Admins may view all stored settings via the /settings URL and modify each one
via /setting/<name>/<value>.

For the scoring evaluation the module 'scoring.py' contains several methods to
evaluate the number of points for a given match and tip. The signature of
these functions is as follows:

    def scoring(initial, match, tip):
        return points

When changing the scoring function the template 'scoring.pt' needs to be
adapted as well.
