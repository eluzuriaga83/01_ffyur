from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract,and_
from _datetime import datetime

db = SQLAlchemy()
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
    #shows = db.relationship('Show', backref=db.backref('venue'), lazy="joined")

   

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
    #shows = db.relationship('Show', backref=db.backref('artist'), lazy="joined")

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
