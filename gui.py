import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.validation import validator, add_validation
from spotify import Spotify
import billboard100
import datetime


GENRE_LIST = ["Pop", "Rock", "Hip Hop/Rap", "Electronic/Dance", "Reggae", "Metal", "Dancehall", "Dubstep"]


@validator
def is_filled(event):
    if len(event.postchangetext) != 0:
        return True
    else:
        return False


@validator
def year_validation(event):
    min_year = datetime.datetime.strptime("1900-01-01", "%Y-%m-%d")
    max_year = datetime.datetime.today() - datetime.timedelta(7)
    try:
        return min_year < datetime.datetime.strptime(event.postchangetext, "%Y-%m-%d") < max_year
    except ValueError:
        return False


class APPGui(tb.Window):

    def __init__(self, master=None, themename="superhero"):
        super().__init__(master, themename=themename)

        self.title("Spotify Playlist Generator")
        self.geometry("800x600")
        self.redirect_url = None

    def clear_frame(self):
        """Clears all widgets from the frame"""
        for widget in self.winfo_children():
            widget.destroy()

    def validate_entries(self, *args):
        for _ in args:
            if not _.validate():
                return False
        return True

    def progressbar(self):
        """Creates progressbar widget + Label and returns it """
        progressbar = tb.Progressbar(self, length=500, maximum=100, value=20, mode="determinate")
        progressbar.pack(pady=10)
        progressbar_label = tb.Label(self, text=f"{progressbar['value']}%", font=("Calibri", 12), bootstyle="default")
        progressbar_label.pack()
        self.update_idletasks()

        return progressbar, progressbar_label

    def update_progressbar(self, progressbar, label, increment_by):
        """Updates the progressbar"""
        progressbar["value"] = progressbar["value"] + increment_by
        label.configure(text=f"{progressbar['value']}%")
        self.update_idletasks()

    def build_playlist_genre(self, username_entry, playlist_entry, genre_entry):
        """Builds the playlist by genre"""
        if self.validate_entries(username_entry, playlist_entry, genre_entry):

            username = username_entry.get()
            playlist_name = playlist_entry.get()
            genre = genre_entry.get()

            progressbar, progressbar_label = self.progressbar()

            new_playlist = Spotify(username, playlist_name, self)
            self.update_progressbar(progressbar, progressbar_label, 10)

            song_names = new_playlist.search_songs_by_genre(genre)
            self.update_progressbar(progressbar, progressbar_label, 20)

            new_playlist.add_songs(song_names, progressbar, progressbar_label)

            self.quit()

    def build_playlist_date(self, username_entry, playlist_entry, date_entry):
        """Build playlist by date"""
        if self.validate_entries(username_entry, playlist_entry, date_entry.entry):
            username = username_entry.get()
            playlist_name = playlist_entry.get()
            date_pick = date_entry.entry.get()

            progressbar, progressbar_label = self.progressbar()

            new_playlist = Spotify(username, playlist_name, self)
            self.update_progressbar(progressbar, progressbar_label, 30)

            song_names = billboard100.get_songs_names(date_pick)
            new_playlist.add_songs(song_names, progressbar, progressbar_label)

            self.quit()

    def get_bygenre_screen(self):
        """Screen for creating a playlist by genre"""

        self.clear_frame()
        label = tb.Label(self, text="Create by Genre", font=("Calibri", 25, "bold"), bootstyle="default")
        label.pack(pady=20)

        genre_menu = tb.Combobox(self, bootstyle="default", values=GENRE_LIST)
        genre_label = tb.Label(self, text="Choose a genre", font=("Calibri", 12), bootstyle="default")
        genre_label.pack(pady=10)
        genre_menu.pack(pady=10)

        playlist_entry = tb.Entry()
        playlist_label = tb.Label(self, text="Enter the name of the playlist",
                                  font=("Calibri", 12), bootstyle="default")
        playlist_label.pack(pady=10)
        playlist_entry.pack(pady=10)

        username_entry = tb.Entry()
        user_name_label = tb.Label(self, text="Enter your Spotify username", font=("Calibri", 12), bootstyle="default")
        user_name_label.pack(pady=10)
        username_entry.pack(pady=10)

        # Add validation to fields
        add_validation(playlist_entry, is_filled, "focusout")
        add_validation(username_entry, is_filled, "focusout")
        add_validation(genre_menu, is_filled, "focusout")

        generate = tb.Button(self, text="Create playlist", bootstyle=SUCCESS, command=lambda: self.build_playlist_genre(
            username_entry, playlist_entry, genre_menu))
        generate.configure(padding=10)
        generate.pack(pady=20)

    def get_bydate_screen(self):
        """Screen for creating a playlist by date"""

        self.clear_frame()
        label = tb.Label(text="CREATE BY DATE", font=("Calibri", 25), bootstyle="default")
        label.pack(pady=20)

        date = tb.DateEntry(self, firstweekday=0, dateformat="%Y-%m-%d")
        date_label = tb.Label(self,
                              text=f"Choose a date between 1/1/1900 and "
                                   f"{(datetime.date.today()-datetime.timedelta(7)).strftime('%x')} ",
                              font=("Calibri", 12), bootstyle="default")

        date_label.pack(pady=10)
        date.pack(pady=10)

        playlist_entry = tb.Entry()
        playlist_label = tb.Label(self, text="Enter the name of the playlist",
                                  font=("Calibri", 12), bootstyle="default")
        playlist_label.pack(pady=10)
        playlist_entry.pack(pady=10)

        username_entry = tb.Entry()
        user_name_label = tb.Label(self, text="Enter your Spotify username", font=("Calibri", 12), bootstyle="default")
        user_name_label.pack(pady=10)
        username_entry.pack(pady=10)

        # Add validation to fields
        add_validation(date.entry, year_validation, "focusout")
        add_validation(playlist_entry, is_filled, "focusout")
        add_validation(username_entry, is_filled, "focusout")

        generate = tb.Button(self, text="Create playlist", bootstyle=SUCCESS, command=lambda: self.build_playlist_date(
            username_entry, playlist_entry, date))
        generate.configure(padding=10)
        generate.pack(pady=20)

    def get_home_screen(self):
        """Home screen with options """

        self.clear_frame()
        label = tb.Label(self, text="Playlist Generator", font=("Calibri", 25, "bold"), bootstyle="default")
        label.pack(pady=40)

        b1 = tb.Button(self, text="Create playlist by genre", bootstyle=(SUCCESS, OUTLINE),
                       command=self.get_bygenre_screen)
        b1.configure(padding=20)
        b1.pack(pady=20)

        b2 = tb.Button(self, text="Create playlist by date", bootstyle=(SUCCESS, OUTLINE),
                       command=self.get_bydate_screen)
        b2.configure(padding=20)
        b2.pack(pady=20)

    def get_redirect_url(self):
        """Pop-up screen fot submitting the redirect URL"""
        popup = tb.Toplevel()
        popup.title("Provide URL")
        popup.geometry("400x200")

        label = tb.Label(popup, text="Paste URL:", font=("Calibri", 12), bootstyle="default")
        label.pack(pady=10)

        url_entry = tb.Entry(popup)
        url_entry.pack(pady=10)

        submit_button = tb.Button(popup, text="Submit", bootstyle=SUCCESS,
                                  command=lambda: self.update_redirect_url(url_entry, popup))
        submit_button.pack(pady=10)

        popup.wait_window()

        return self.redirect_url

    def update_redirect_url(self, url, popup):
        """Saves the authorization code so it can be passed"""
        self.redirect_url = url.get()
        popup.destroy()

    def show_error_message(self, error_msg):
        Messagebox.show_error(error_msg, "Something went wrong", self)
        self.get_home_screen()
