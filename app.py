#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from email.policy import default
import json
import sys
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import app, db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
migration = Migrate(app, db)


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    for cands in Venue.query.with_entities(Venue.city, Venue.state).order_by(Venue.state).distinct():
        cityandstatelist = {
            "city": cands.city,
            "state": cands.state,
        }
        venuelist = []
        for venue in Venue.query.filter_by(city=cands.city, state=cands.state).all():
            lists = {
                "id": venue.id,
                "name": venue.name,
            }
            venuelist.append(lists)
        cityandstatelist['venues'] = venuelist
        data.append(cityandstatelist)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = "%"+request.form.get('search_term', '')+"%"
    venues = Venue.query.filter(Venue.name.ilike(search_term))
    results = {
        "count": venues.count(),
        "data": []
    }
    for venue in venues:
        data = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 0,
        }
        results["data"].append(data)
    return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venu = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    for show in Show.query.filter_by(venues_id=venu.id):
        if show.start_time < datetime.today():
            past_show = {
                "artist_id": show.artists.id,
                "artist_name": show.artists.name,
                "artist_image_link": show.artists.image_link,
                "start_time": show.start_time
            }
            past_shows.append(past_show)
            past_shows_count += 1
        else:
            upcoming_show = {
                "artist_id": show.artists.id,
                "artist_name": show.artists.name,
                "artist_image_link": show.artists.image_link,
                "start_time": show.start_time
            }
            upcoming_shows.append(upcoming_show)
            upcoming_shows_count += 1
    venue = {
        "id": venu.id,
        "name": venu.name,
        "genres": venu.genres,
        "address": venu.address,
        "city": venu.city,
        "state": venu.state,
        "phone": venu.phone,
        "website": venu.website_link,
        "facebook_link": venu.facebook_link,
        "seeking_talent": venu.seeking_talent,
        "image_link": venu.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }
    data = list(filter(lambda d: d['id'] ==
                venue_id, [venue]))[0]
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        form = VenueForm()
        if form.validate_on_submit():
            if form.seeking_talent.data:
                venue = Venue(
                    name=form.name.data,
                    city=form.city.data,
                    address=form.address.data,
                    state=form.state.data,
                    phone=form.phone.data,
                    genres=form.genres.data,
                    facebook_link=form.facebook_link.data,
                    image_link=form.image_link.data,
                    website_link=form.website_link.data,
                    seeking_talent=form.seeking_talent.data,
                    seeking_description=form.seeking_description.data,)
                db.session.add(venue)
                db.session.commit()
            else:
                venue = Venue(
                    name=form.name.data,
                    city=form.city.data,
                    address=form.address.data,
                    state=form.state.data,
                    phone=form.phone.data,
                    genres=form.genres.data,
                    facebook_link=form.facebook_link.data,
                    image_link=form.image_link.data,
                    website_link=form.website_link.data,
                    seeking_description=form.seeking_description.data,)
                db.session.add(venue)
                db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + form.name.data + ' a été ajouté')
        else:
            return render_template('submit.html', form=form)
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('Venue ' + form.name.data +
              ' n\'a pas été crée. Une erreur s\'est produite.')
    finally:
        db.session.close()
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = []
    for artists in Artist.query.with_entities(Artist.id, Artist.name).order_by(db.desc(Artist.id)):
        artist = {
            "id": artists.id,
            "name": artists.name,
        }
        data.append(artist)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = "%"+request.form.get('search_term', '')+"%"
    artists = Artist.query.filter(Artist.name.ilike(search_term))
    results = {
        "count": artists.count(),
        "data": []
    }
    for artist in artists:
        data = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": 0,
        }
        results["data"].append(data)
    return render_template('pages/search_artists.html', results=results, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    for show in Show.query.filter_by(artists_id=artist.id):
        if show.start_time < datetime.today():
            past_show = {
                "venue_id": show.venues.id,
                "venue_name": show.venues.name,
                "venue_image_link": show.venues.image_link,
                "start_time": show.start_time
            }
            past_shows.append(past_show)
            past_shows_count += 1
        else:
            upcoming_show = {
                "venue_id": show.venues.id,
                "venue_name": show.venues.name,
                "venue_image_link": show.venues.image_link,
                "start_time": show.start_time
            }
            upcoming_shows.append(upcoming_show)
            upcoming_shows_count += 1
    artist_select = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }
    data = list(filter(lambda d: d['id'] ==
                artist_id, [artist_select]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist_select = Artist.query.get(artist_id)
    form = ArtistForm()
    artist = {
        "id": artist_select.id,
        "name": artist_select.name,
        "genres": artist_select.genres,
        "city": artist_select.city,
        "state": artist_select.state,
        "phone": artist_select.phone,
        "website": artist_select.website_link,
        "facebook_link": artist_select.facebook_link,
        "seeking_venue": artist_select.seeking_venue,
        "seeking_description": artist_select.seeking_description,
        "image_link": artist_select.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        form = ArtistForm()
        if form.validate_on_submit():
            artist = Artist.query.get(artist_id)
            if form.seeking_venue.data:
                artist.name = form.name.data
                artist.city = form.city.data
                artist.state = form.state.data
                artist.phone = form.phone.data
                artist.genres = form.genres.data
                artist.facebook_link = form.facebook_link.data
                artist.image_link = form.image_link.data
                artist.website_link = form.website_link.data
                artist.seeking_venue = form.seeking_venue.data
                artist.seeking_description = form.seeking_description.data
                db.session.add(artist)
                db.session.commit()
                flash('Artist ' + form.name.data + ' a été mis à jour')
                return redirect(url_for('show_artist', artist_id=artist_id))
            else:
                artist.name = form.name.data
                artist.city = form.city.data
                artist.state = form.state.data
                artist.phone = form.phone.data
                artist.genres = form.genres.data
                artist.facebook_link = form.facebook_link.data
                artist.image_link = form.image_link.data
                artist.website_link = form.website_link.data
                artist.seeking_description = form.seeking_description.data
                db.session.add(artist)
                db.session.commit()
            flash('Artist ' + form.name.data + ' a été mis à jour')
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            return render_template('forms/edit_artist.html', form=form)
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('Artist ' + form.name.data +
              ' n\'a pas été mise à jour. Une erreur s\'est produite.')
    finally:
        db.session.close()


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venu = Venue.query.get(venue_id)
    form = VenueForm()
    venue = {
        "id": venu.id,
        "name": venu.name,
        "genres": venu.genres,
        "address": venu.address,
        "city": venu.city,
        "state": venu.state,
        "phone": venu.phone,
        "website": venu.website_link,
        "facebook_link": venu.facebook_link,
        "seeking_talent": venu.seeking_talent,
        "seeking_description": venu.seeking_description,
        "image_link": venu.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm()
        if form.validate_on_submit():
            venue = Venue.query.get(venue_id)
            if form.seeking_talent.data:
                venue.name = form.name.data
                venue.city = form.city.data
                venue.address = form.address.data
                venue.state = form.state.data
                venue.phone = form.phone.data
                venue.genres = form.genres.data
                venue.facebook_link = form.facebook_link.data
                venue.image_link = form.image_link.data
                venue.website_link = form.website_link.data
                venue.seeking_talent = form.seeking_talent.data
                venue.seeking_description = form.seeking_description.data
                db.session.add(venue)
                db.session.commit()
                flash('Venue ' + form.name.data + ' a été mis à jour')
                return redirect(url_for('show_venue', venue_id=venue_id))
            else:
                venue.name = form.name.data
                venue.city = form.city.data
                venue.address = form.address.data
                venue.state = form.state.data
                venue.phone = form.phone.data
                venue.genres = form.genres.data
                venue.facebook_link = form.facebook_link.data
                venue.image_link = form.image_link.data
                venue.website_link = form.website_link.data
                venue.seeking_description = form.seeking_description.data
                db.session.add(venue)
                db.session.commit()
            flash('Venue ' + form.name.data + ' a été mis à jour')
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            return render_template('forms/edit_venue.html', form=form)
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('Venue ' + form.name.data +
              ' n\'a pas été mise à jour. Une erreur s\'est produite.')
    finally:
        db.session.close()

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        form = ArtistForm()
        if form.validate_on_submit():
            if form.seeking_venue.data:
                artist = Artist(
                    name=form.name.data,
                    city=form.city.data,
                    state=form.state.data,
                    phone=form.phone.data,
                    genres=form.genres.data,
                    facebook_link=form.facebook_link.data,
                    image_link=form.image_link.data,
                    website_link=form.website_link.data,
                    seeking_venue=form.seeking_venue.data,
                    seeking_description=form.seeking_description.data,)
                db.session.add(artist)
                db.session.commit()
            else:
                artist = Artist(
                    name=form.name.data,
                    city=form.city.data,
                    state=form.state.data,
                    phone=form.phone.data,
                    genres=form.genres.data,
                    facebook_link=form.facebook_link.data,
                    image_link=form.image_link.data,
                    website_link=form.website_link.data,
                    seeking_description=form.seeking_description.data,)
                db.session.add(artist)
                db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + form.name.data + ' a été ajouté')
        else:
            return render_template('submit.html', form=form)
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('Artist ' + form.name.data +
              ' n\'a pas été crée. Une erreur s\'est produite.')
    finally:
        db.session.close()
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    for shows in Show.query.order_by(db.desc(Show.start_time)):
        show = {
            "venue_id": shows.venues.id,
            "venue_name": shows.venues.name,
            "artist_id": shows.artists.id,
            "artist_name": shows.artists.name,
            "artist_image_link": shows.artists.image_link,
            "start_time": shows.start_time
        }
        data.append(show)
    return render_template('pages/shows.html', shows=data)

    # CREATE SHOW


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        form = ShowForm()
        if form.validate_on_submit():
            show = Show(
                artists_id=form.artist_id.data,
                venues_id=form.venue_id.data,
                start_time=form.start_time.data,)
            db.session.add(show)
            db.session.commit()
            flash('Le show a été crée!')
        else:
            return render_template('submit.html', form=form)
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('Le show n\'a pas été crée ! Un problème est survenu')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
