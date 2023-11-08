# manga_dl
This is designed to download manga's direct from ether [manhuaes.com](https://manhuaes.com/), [manhuaaz.com](https://manhuaaz.com/), [manhuaus.com](https://manhuaus.com/), [mangaread.com](https://mangaread.com/) or [webtoons.com](https://webtoons.com/)

## Usage

First clone the repo
```bash
git clone https://github.com/thezak48/manga_dl
cd manga_dl
```

Install the requirements
```bash
pip install -r requirements.txt
```

Run manga_dl.py
```bash
python3 manga_dl.py manga [optional] /path/to/manga/folder
```

`manga` is the the url of the manga from ether [manhuaes.com](https://manhuaes.com/) [manhuaaz.com](https://manhuaaz.com/) [manhuaus.com](https://manhuaus.com/) [mangaread.com](https://mangaread.com/) [webtoons.com](https://webtoons.com/) websites. Please see `manga.example.txt` for an example of what is required.

`manga` can also accept a txt file containing a list of names
see [manga.txt](https://github.com/thezak48/manga_dl/blob/main/manga.example.txt) for an example of the file, to use it just do
```bash
python3 manga_dl.py manga.txt [optional] /path/to/manga/folder
```


### Advanced Usage
There is an optional argument to enable the ability to download all pages of a chapter at once. Just pass the arg `-mt` after the `manga` for example

```bash
python3 manga_dl.py manga -mt /path/to/manga/folder
```

#### Run as Systemd Service
1. Edit the `User`, `Group`, `WorkingDirectory` and `ExecStart` in `manga_dl.service` to the correct values<br/>
2. Copy `manga_dl.service` and `manga_dl.timer` to `/etc/systemd/system/`
3. Execute these commands to enable the service and timer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable manga_dl.service
sudo systemctl start manga_dl.service
sudo systemctl enable manga_dl.timer
sudo systemctl start manga_dl.timer
```
You can check if the timer is running with `sudo systemctl list-timers` and it should show something like this:
`Mon 2023-11-19 23:51:49 CEST 3min 1s left  n/a                          n/a                manga_dl.timer      manga_dl.service`