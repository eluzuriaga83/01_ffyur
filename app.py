#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from datetime import datetime
import dateutil.parser
from sqlalchemy import func
from _datetime import date
from sqlalchemy import extract,and_


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(250))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(800))
    #show = db.relationship('Show', backref=('artist'),lazy=True, passive_deletes=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)#db.Column(db.String(120))
    website = db.Column(db.String(250))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(800))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id', ondelete = 'CASCADE'), nullable=False)
    venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id', ondelete = 'CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    # relationships
    artist = db.relationship(Artist,backref=db.backref('shows', cascade='all, delete'))
    venue = db.relationship(Venue,backref=db.backref('shows', cascade='all, delete'))

class Album(db.Model):
    __tablename__ = 'Album'

    id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id', ondelete = 'CASCADE'), nullable=False)
    name = db.Column(db.String(120))
    year = db.Column(db.String(4))
    # relationships
    artist = db.relationship(Artist,backref=db.backref('album', cascade='all, delete'))
    
class Song(db.Model):
    __tablename__ = 'Song'

    id = db.Column(db.Integer, primary_key = True)
    album_id = db.Column('album_id', db.Integer, db.ForeignKey('Album.id', ondelete = 'CASCADE'), nullable=False)
    title = db.Column(db.String(120))
    
    # relationships
    album = db.relationship(Album,backref=db.backref('song', cascade='all, delete'))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en_US')

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  data = []
  for area in areas:
    areas = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in areas:
      venue_data.append({
        'id':venue.id,
        'name':venue.name, 
        'num_upcoming_shows': len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
      })
      data.append({
        'city':area.city,
        'state':area.state,
        'venues':venue_data
      })
    print(data)
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = ''
  if request.method == "POST":
    search_term = request.form.get('search_term', '')

  response={}
  data=[]
  result = db.session.query(Venue).filter(func.lower(Venue.name).contains(search_term.lower(), autoescape=True)).all()
  
  for venue in result:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(db.session.query(Show).join(Venue).filter(Show.venue_id == venue.id,Show.start_time > datetime.now()).all()),
    })

  response={
    "count": len(result),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  past_shows=[]
  upcoming_shows=[]
  #getting the venue under the id
  venue1 = Venue.query.get(venue_id)
  #Create a query that join the tree tables and filter by venueid, artist id and start time is less that the actual time
  past = db.session.query(Show).join(Artist).join(Venue).filter(Show.venue_id==venue_id,Show.artist_id == Artist.id,Show.start_time < datetime.now()).all()
  for past_show in past:
    past_shows.append({
      'artist_id': past_show.artist.id,
      'artist_name': past_show.artist.name,
      'artist_image_link':past_show.artist.image_link,
      'start_time': past_show.start_time.strftime("%m-%d-%Y %H:%M:%S")
    })

  #Create a query that join the tree tables and filter by venueid, artist id and start time is greatess that the actual time
  upcoming = db.session.query(Show).join(Artist).join(Venue).filter(Show.venue_id == venue_id,Show.artist_id == Artist.id,Show.start_time > datetime.now()).all() 
  #db.session.query(Artist, Show).join(Show).join(Venue).filter(Show.venue_id == venue_id,Show.artist_id == Artist.id,Show.start_time > datetime.now()).all() 
  for upcoming_show in upcoming:
    print('upcoming', upcoming_show.artist.id,upcoming_show.artist.name)
    upcoming_shows.append({
      'artist_id': upcoming_show.artist.id,
      'artist_name': upcoming_show.artist.name,
      'artist_image_link':upcoming_show.artist.image_link,
      'start_time': upcoming_show.start_time.strftime("%m-%d-%Y %H:%M:%S")
    })

  data.append({
    "id": venue1.id,
    "name": venue1.name,
    "genres": venue1.genres,
    "address": venue1.address,
    "city":venue1.city,
    "state": venue1.state,
    "phone": venue1.phone,
    "website": venue1.website,
    "facebook_link": venue1.facebook_link,
    "seeking_talent": venue1.seeking_talent,
    "seeking_description": venue1.seeking_description,
    "image_link": venue1.image_link,
    "upcoming_shows": upcoming_shows,    
    "past_shows": past_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    
  })
  
  data1 = list(data)[0]
  print(data1)
  return render_template('pages/show_venue.html', venue=data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = VenueForm(request.form,meta={'csrf': False})
  if form.validate():
    try:
        venue = Venue(name=form.name.data, 
        city = form.city.data, 
        state = form.state.data, 
        address = form.address.data,
        phone = form.phone.data, 
        genres = form.genres.data, 
        website =  form.website.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        seeking_description = form.seeking_description.data,
        seeking_talent = form.seeking_talent.data)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + form.name.data + ' was successfully listed!')
    
    except ValueError as e:
        print(e)
        error = True
        db.session.rollback() 
        flash('An error occurred. Venue '+ form.name.data + ' could not be listed.')
        not_found_error(400)
      
    finally:
        print('final')
        db.session.close()
  
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
      
  return render_template('pages/home.html')

 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  print('delete')
  try:
      db.session.query(Venue).filter(Venue.id == venue_id).delete()
      db.session.commit()
      flash('The venue was removed successfully.')
  except ValueError as e:
      print(e)
      error = True
      db.session.rollback() 
      flash('The venue could not be remove.')
      not_found_error(400)
    
  finally:
      print('final')
      db.session.close()
  
  
  #return render_template('pages/home.html')
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = db.session.query(Artist).all()
  
  # TODO: replace with real data returned from querying the database
  data = []
  for artist in artists:{
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  }

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = ''
  if request.method == "POST":

    search_term = request.form.get('search_term', '')
    print(search_term)
  response={}
  data=[]
  result = db.session.query(Artist).filter(func.lower(Artist.name).contains(search_term.lower(), autoescape=True)).all()
  #filter(Artist.name.like('%'+ search_term + '%')).all()
  #iterate the result to add each item to the data list
  for artist in result:
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(db.session.query(Show).join(Artist).join(Venue).filter(Show.venue_id == Venue.id,Show.artist_id == artist.id,Show.start_time > datetime.now()).all()),
    })

  response={
    "count": len(result),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = {}
  past_shows=[]
  upcoming_shows=[]
  albums_songs=[]
  #getting the Artist under the id
  artist = db.session.query(Artist).get(artist_id)
  
  #getting the past shows
  past = db.session.query(Show).join(Venue).join(Artist).filter(Show.venue_id==Venue.id,Show.artist_id == artist_id,Show.start_time < datetime.now()).all()
  print(past)
  for past_show in past:
    past_shows.append({
      'venue_id': past_show.venue.id,
      'venue_name': past_show.venue.name,
      'venue_image_link':past_show.venue.image_link,
      'start_time': past_show.start_time.strftime("%m-%d-%Y %H:%M:%S")
    })
  #getting the new shows 
  upcoming = db.session.query(Show).join(Venue).join(Artist).filter(Show.venue_id==Venue.id,Show.artist_id == artist_id,Show.start_time > datetime.now()).all() 
  for upcoming_show in upcoming:
    upcoming_shows.append({
      'venue_id': upcoming_show.venue.id,
      'venue_name': upcoming_show.venue.name,
      'venue_image_link':upcoming_show.venue.image_link,
      'start_time': upcoming_show.start_time.strftime("%m-%d-%Y %H:%M:%S")
    })
  
  albums = db.session.query(Album).filter(Album.artist_id==artist_id).all()
  for album in albums:
    songs = db.session.query(Song).join(Album).filter(Song.album_id==album.id).all()
    albums_songs.append({
      "id": album.id,
      "name": album.name,
      "songs": [{
        "id_song": song.id,
        "title": song.title
      }for song in songs] 
    })

  print('albums_songs', albums_songs)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows,
    "upcoming_shows_count": len(upcoming_shows),
    "past_shows_count": len(past_shows),
    "albums": albums_songs
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  result = db.session.query(Artist).get(artist_id)
  
  artist={
    "id": result.id,
    "name": result.name,
    "genres": result.genres,
    "city": result.city,
    "state": result.state,
    "phone": result.phone,
    "website": result.website,
    "image_link": result.image_link,
    "facebook_link": result.facebook_link,
    "seeking_venue": result.seeking_venue,
    "seeking_description": result.seeking_description,
    
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form,meta={'csrf': False})
  if form.validate():
    try:
        #Query to update the artist by id
        db.session.query(Artist).filter(Artist.id == artist_id).update({'name': form.name.data,
        'city':form.city.data, 
        'state':form.state.data, 
        'phone':form.phone.data, 
        'genres':form.genres.data, 
        'website':form.website.data,
        'image_link':form.image_link.data,
        'facebook_link':form.facebook_link.data,
        'seeking_description': form.seeking_description.data,
        'seeking_venue': form.seeking_venue.data 
        })
        db.session.commit() 

        flash('Artist ' + form.name.data + ' was successfully updated!')
    except ValueError as e:
        print(e)
        error = True
        db.session.rollback() #+ request.get_json()['name'] + 
        flash('An error occurred. Artist ' + ' could not be updated.')
        not_found_error(400)
      
    finally:
        db.session.close()
  
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))

  return redirect(url_for('show_artist', artist_id=artist_id))


#Delete Artists
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  print('delete')
  try:
      db.session.query(Artist).filter(Artist.id == artist_id).delete()
      db.session.commit()
      flash('The Artist was removed successfully.')
  except ValueError as e:
      print(e)
      error = True
      db.session.rollback() 
      flash('The Artist could not be remove.')
      not_found_error(400)
    
  finally:
      print('final')
      db.session.close()
  
  
  #return render_template('pages/home.html')
  return redirect(url_for('Artists'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form,meta={'csrf': False})
  if form.validate():
    try:
 
        db.session.query(Venue).filter(Venue.id == venue_id).update({'name': form.name.data,
        'city':form.city.data, 
        'state':form.state.data, 
        'phone':form.phone.data, 
        'genres':form.genres.data, 
        'website':form.website.data,
        'image_link':form.image_link.data,
        'facebook_link':form.facebook_link.data,
        'seeking_description': form.seeking_description.data,
        'seeking_talent': form.seeking_talent.data 
        })
        db.session.commit() 

        flash('Venue ' + form.name.data + ' was successfully updated!')
    except ValueError as e:
        print(e)
        error = True
        db.session.rollback() #+ request.get_json()['name'] + 
        flash('An error occurred. Venue ' + ' could not be updated.')
        not_found_error(400)
      
    finally:
        db.session.close()
  
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
   
    form = ArtistForm(request.form,meta={'csrf': False})
    if form.validate():
      try:
          artist = Artist(name=form.name.data, 
          city=form.city.data, 
          state=form.state.data, 
          phone=form.phone.data, 
          genres=form.genres.data, 
          website = form.website.data,
          image_link = form.image_link.data,
          facebook_link=form.facebook_link.data,
          seeking_description=form.seeking_description.data,
          seeking_venue= form.seeking_venue.data 
          )
          db.session.add(artist)
          db.session.commit()
          flash('Artist ' + form.name.data + ' was successfully listed!')
      except ValueError as e:
          print(e)
          error = True
          db.session.rollback() #+ request.get_json()['name'] + 
          flash('An error occurred. Artist ' + form.name.data +  ' could not be listed.')
          not_found_error(400)
        
      finally:
          print('final')
          db.session.close()
    
    else:
      message = []
      for field, err in form.errors.items():
          message.append(field + ' ' + '|'.join(err))
      flash('Errors ' + str(message))
        
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  venues = db.session.query(Venue).join(Show).filter(Show.venue_id==Venue.id,Show.start_time > datetime.now() ).distinct(Venue.id).all()
  print(venues)
  #display show by venue
  venue_data=[]
  for venue in venues:
    show_data = []
    #select the shows by venue
    shows = db.session.query(Show).join(Artist).join(Venue).filter(Show.venue_id==venue.id, Show.artist_id==Artist.id, Show.start_time > datetime.now()).all()
    upcoming = db.session.query(Show).join(Venue).filter(Show.start_time > datetime.now(),Show.venue_id==venue.id).all()
    
    for show in shows:  
      show_data.append({
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%m-%d-%Y %H:%M:%S") #"2019-05-21T21:30:00.000Z"
      })
    #add the shows by venue and the number of upcoming shows
    venue_data.append({
      "venue_name": venue.name,
      "num_upcoming_shows": len(upcoming),
      "shows": show_data
    })
  
  return render_template('pages/shows.html', venues=venue_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
 
  form = ShowForm(request.form,meta={'csrf': False})
  if form.validate():
    try:
        date_time_obj = form.start_time.data 
        #Query to help to find out if there are shows in the same day and hour
        artist_shows = db.session.query(Show).join(Artist).filter(and_(Show.artist_id==form.artist_id.data,
        func.DATE(Show.start_time) == date_time_obj.date(), extract('hour', Show.start_time)==date_time_obj.hour)).first() 
        #if there are not results, the show would be added correctly
        if(artist_shows== None):
          show = Show(
            artist_id = form.artist_id.data,
            venue_id = form.venue_id.data,
            start_time= date_time_obj 
          )
          db.session.add(show)
          db.session.commit()
          flash('Show was successfully listed!')
        else:
          flash('The artist has already booked an event at the same time and hour')  
    except ValueError as e:
        print(e)
        error = True
        db.session.rollback() 
        #if there are a mistake, a message would be displayed
        flash('The Show could not be listed.')
        not_found_error(400)
      
    finally:
        print('final')
        db.session.close()
  
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
      
  return render_template('pages/home.html')
#Albums
@app.route('/albums/create', methods=['GET'])
def create_album_form():
  form = AlbumForm()
  return render_template('forms/new_album.html', form=form)

@app.route('/albums/create', methods=['POST'])
def create_album_submission():

  form = AlbumForm(request.form,meta={'csrf': False})
  if form.validate(): #validate that the form exist
    try: #create a object type Album 
        album = Album(
            artist_id = form.artist_id.data,
            name = form.name.data,
            year = form.year.data 
         )
        db.session.add(album)
        db.session.commit()

        flash('Album ' + form.name.data + ' was successfully created!')
    except ValueError as e:
        print(e)
        error = True
        db.session.rollback() 
        flash('An error occurred. Album ' + form.name.data +  ' could not be listed.')
        not_found_error(400)
      
    finally:
        print('final')
        db.session.close()
  
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
      
  return render_template('pages/home.html')

'''@app.route('/albums/<int:album_id>')
def show_album(album_id):
  data =[]
  artist = db.session.query(Artist).join(Album).filter(Album.id==album_id, Album.artist_id==Artist.id).first()
  album = db.session.query(Album).filter(Album.id == album_id).first()
  data={
    'album_id': album.id,
    'name': album.name,
    'artist_name': artist.name
  }

  return render_template('pages/show_album.html', album=data)'''
#Songs
@app.route('/songs/create', methods=['GET'])
def create_song_form():
  form = SongForm()
  return render_template('forms/new_song.html', form=form)

@app.route('/songs/create', methods=['POST'])
def create_song_submission():
#create a new record with the song in a specific album
  form = SongForm(request.form,meta={'csrf': False})
  if form.validate():
    try:
        song = Song(
            album_id = form.album_id.data,
            title = form.title.data,
        )
        db.session.add(song)
        db.session.commit()

        flash('Song ' + form.title.data + ' was successfully created!')
    except ValueError as e:
        print(e)
        error = True
        db.session.rollback() 
        flash('An error occurred. Song ' + form.title.data +  ' could not be listed.')
        not_found_error(400)
      
    finally:
        print('final')
        db.session.close()
  
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
      
  return render_template('pages/artists.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
