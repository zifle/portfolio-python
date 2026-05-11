# Photo Portfolio project

This is my personal project for my photography portfolio.

It's intended to display, and work, as I feel is pleasing and intuitive, 
and so not much thought have been put into making the project extensible,
or easily modifiable.


## Setup

### Backend

The backend is written in Python using Django.

The required packages are listed in `requirements.txt`, install them by running
```shell
$ pip install -r requirements.txt
```

Environment variables are loaded from the `.env` file, you can start by copying the examples file
```shell
$ cp .env-example .env
```
- You should set the `SECRET_KEY`, and the host you plan to serve the site from (for testing, something like 
`portfolio.dev` works well, if it's set up in your hosts file).
- Make sure to set the database you want to use, in the `/mysite/settings.py` file
  - I've kept the default SQLite database, without a .env option, so you do not need to change it if that's your use-case

Once packages are installed, and the database is set up, make sure you run the migrations;
```shell
$ ./manage.py migrate
```

Then the site is ready to be served. For development, I've simply used the built-in webserver
to host, so it's likely (I can almost guarantee it) that changes will have to be made if you're
using a proper webserver to host the site. As it is, the app will serve the `/frontend/dist/index.html`
file if the route is not otherwise recognised.

Note also, however, that the project default settings add the `/static/uploads` folder to the
`STATICFILES_DIRS` setting, allowing python to serve the uploaded image files through its
webserver. This should _not_ be enabled on production, but instead be handled by the production-ready
server sitting in front of the app. For testing, it works fine.

Run the development/testing server with;
```shell
$ ./manage.py runserver
```

### Frontend

The frontend is built in Vue, with bootstrap.

Open the `frontend` folder, install the packages, and run a build:
```shell
$ cd frontend
$ npm install
$ npm run build
```
The project will be built in the `/frontend/dist` folder, which houses the main index.html

## Usage

By default, no data is seeded to the database, so it's up to you what you add to it.

### Admin interface

#### Setup

To enter the admin page, make sure to first create an admin user;
```shell
$ ./manage.py createsuperuser
```
You will be using the `username` and `password` to log in to the admin interface, so make sure to
enter something you can remember.

After creating an admin account, navigate to the login page (or any of the admin pages in the browser);
```
http://portfolio.dev:8000/login
```
You should be greeted by a login form, after which you will be shown the `/admin/albums` page.

#### Categories
While it's not strictly necessary to set up categories, you may want to head there first,
to have some structure to your albums.

In this portfolio, categories are simply used as a way to create a sub-menu. Albums do not need
to be attached to a category, and without one, it'll simply be shown as its own menu item in the
root menu.

The order property of the category, allow you some control of where it's displayed in the menu,
however note that categories are always displayed before "root" albums.

Once a category is created, it can be edited or deleted easily - Deleting a category will not
remove attached albums, but please note that there is no confirmation, nor an undo function, to it.

To quickly edit a category, simply double-click the name or the order, and press `enter` when you're done.
You can cancel by pressing `esc`, with either of the fields active.

#### Locations
Much like categories, locations are not a necessary feature of albums, but it can be helpful to
set some up beforehand, if you plan on using them.

Locations consist of a name, and some coordinates. Create a location by setting the name, and a
comma-separated `lat,long` value.

Existing locations can be edited in the same way as categories, by double-clicking and confirming
with `enter`, or cancelling with `esc`

#### Album creation
To create your first album, go to the `/admin/albums/create` page, and start filling out the information.

##### Image upload
It's recommended that you _start_ with uploading your image set. Simply drag-and-drop _all_ of your image
files from your desktop, to the window. There should be a big `+` in the middle of the page, indicating
that you can drop the files. Once they're dropped, they'll immediately start uploading in the background,
so you can start filling the album metadata at the same time.

##### Album metadata
If you've opted to upload your images first, you can skip the `Start date`, `End date`, and `Location`
for now. The system reads the EXIF data from your images automatically, and uses the `date_taken`
property of each image, to automatically set a start and end date.

Similarly, if the images are geo-tagged, and you've set up one or more locations, the system
automatically finds the approximate centre of the photos, and uses that to find the nearest locations.
Only locations within 10km of the approximated centre will be considered, and distances will be displayed
in the options once it's loaded.

Once images are uploaded, and you're happy with your metadata, you can save the album, and you'll 
automatically get redirected to the album edit page, for the same album. The new album should also
instantly appear in the menu at the top (it will be within a category, if set).

##### Image reordering

If you're unhappy with the order of the images, you can drag them around, until you're happy.
Note that due to how the masonry layout on the user-side album view works, the images will not
necessarily be strictly placed in the order you designate, so play around with something that
works for your images.

Drop the image on either side of another, to place the image either before or after the target.

When you've reordered any images, make sure to save the changes by clicking the `Save Album` button.

##### Album publication
Note that albums can be published, or not. Unpublished albums will not appear on the user-side,
but will still be displayed for logged-in admins.
This is also the case for categories, where a category without any albums, or with only unpublished
albums, will not be displayed in the menu.

You can change the publication of your album simply by checking/unchecking the `Published` checkbox
on the album edit page, or clicking the published toggle button in the albums overview (at `/admin/albums`).

##### Text boxes
In addition to images, albums can also contain text boxes, which will be placed in the same grid
as the images.

To create a text box, simply click the `+ Add Text` button at the end of the images display section
(you may have to scroll down to the bottom).

It'll create a new text box, with some sample text. Double-click it to start editing the text, and
when you're done, simply defocus the box, and the text will get saved automatically. Make sure you
also save the album, to properly attach the new text, if you created a new box. If you're editing
and existing, already attached box, you don't strictly need to save the album again, but it's
recommended to be sure.

Like with images, text boxes can also be reordered to get the desired ordering on the view page, but
the same caveats about masonry layout also applies to text, in that you cannot rely on the order 100%.
For this reason, you should avoid using them to describe specific images, and instead use them for
story-telling.

##### Image descriptions
If you want to add a description to an image, you can simply double-click it in the album edit page,
and a text box below the image will show up, and be focused. Similarly to text boxes, simply enter
the text you wish, and defocus the field to save.

As of writing, the image descriptions are only used as `alt` text on the `<img>` tags, so they have
limited functionality, and thus are also not displayed in the admin interface.

Note that image descriptions are set on the image model itself, so if an image is shared across multiple
albums, the description also will be.

##### Image duplications
When uploading images, the system starts by checking the EXIF data of the uploaded image.
Specifically, the `date_taken` attribute is checked, and combined with the uploaded filename, the
database is checked for any duplications, before handling the image further.

This saves on storage, and allows multiple albums to share images. Thus, if you want to reuse an
already uploaded image, don't worry about any extra storage, or image caching. 
Only the bandwidth will be duplicated.

For this reason, when multiple duplicate images are uploaded, the upload itself may also appear
impossibly fast (assuming the upload itself is quick), but that's simply because we can skip
the step of resizing multiple images files, as it's already been done once.

##### Album item deletion
To remove an item (image or text box) from an album, simply click the red `x` in the top right corner
of the element. Note that there is no confirmation, or undo, but if you've removed an image by mistake,
simply drop it into the album again, and it'll reuse the same instance as before.

### User/Guest site
The user-facing site does not contain a lot by default.
If you've not set up any albums, only the `/home` page will be available, and it's not set up to contain
much information.

If you're logged in as admin, and want to check what a guest would see, simply click the `➜]` button
next to the `Admin` at the end of the menu.

The menu is automatically generated, based on published albums, and categories.
Click on an album to view it. Depending on the metadata specified on the album, the page will be automatically
built to display more or less data.

The album title, date (start and end, if they're not the same), and location, will be in the header section
of the page, followed by the album description below it.

Just underneath the description, a list of album tags will be displayed. These are automatically generated
based on various properties on the album, and the attached images.
 - Album category
 - Album location
 - One-day/Multiple days, indicating if the album spans one or more days
 - Cameras used to take the photos
 - Lenses used to take the photos

The latter two are automatically fetched from the images EXIF data when uploaded.