# manhua-dl
This is designed to download manhua's direct from ether [manhuaes.com](https://manhuaes.com/), [manhuaaz.com](https://manhuaaz.com/), [manhuaus.com](https://manhuaus.com/), [mangaread.com](https://mangaread.com/) or [webtoons.com](https://webtoons.com/)

## Usage

First clone the repo
```bash
git clone https://github.com/thezak48/manhua-dl
cd manhua-dl
```

Install the requirements
```bash
pip install -r requirements.txt
```

Run manhua-dl.py
```bash
python3 manhua-dl.py manhua [optional] /path/to/manhua/folder
```

`manhua` is the the url of the manhua from ether [manhuaes.com](https://manhuaes.com/) [manhuaaz.com](https://manhuaaz.com/) [manhuaus.com](https://manhuaus.com/) [mangaread.com](https://mangaread.com/) [webtoons.com](https://webtoons.com/) websites. Please see `manhua.example.txt` for an example of what is required.

`manhua` can also accept a txt file containing a list of names
see [manhua.txt](https://github.com/thezak48/manhua-dl/blob/main/manhua.txt) for an example of the file, to use it just do
```bash
python3 manhua-dl.py manhua.txt [optional] /path/to/manhua/folder
```


### Advanced Usage
There is an optional argument to enable the ability to download all pages of a chapter at once. Just pass the arg `-mt` after the `manhua` for example

```bash
python3 manhua-dl.py manhua -mt /path/to/manhua/folder
```

#### Run as Systemd Service
1. Edit the `User`, `Group`, `WorkingDirectory` and `ExecStart` in `manhua-dl.service` to the correct values<br/>
2. Copy `manhua-dl.service` and `manhua-dl.timer` to `/etc/systemd/system/`
3. Execute these commands to enable the service and timer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable manhua-dl.service
sudo systemctl start manhua-dl.service
sudo systemctl enable manhua-dl.timer
sudo systemctl start manhua-dl.timer
```
You can check if the timer is running with `sudo systemctl list-timers` and it should show something like this:
`Mon 2023-11-19 23:51:49 CEST 3min 1s left  n/a                          n/a                manhua-dl.timer      manhua-dl.service`