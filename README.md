# manga_dl
This is designed to download manga's direct from ether 
- [manhuaes.com](https://manhuaes.com/)
- [manhuaaz.com](https://manhuaaz.com/)
- [manhuaus.com](https://manhuaus.com/)
- [manhuaus.org](https://manhuaus.org/)
- [mangaread.org](https://mangaread.org/)
- [kaiscans.com](https://kaiscans.com/)
- [mangakaklot.com](https://mangakakalot.com/)
- [webtoons.com](https://webtoons.com/)
- [lhtranslation.net](https://lhtranslation.net/)
- [topmanhua.com](https://topmanhua.com)

## Usage

Deploy manga_dl using the docker-compose example provided.

## Config File

1. Create a `config.ini` file in the data directory. See the `config.example.ini` file
2. If no `config.ini` file exists when running, manga_dl will make the file and defaults will be used.

### Config Options


`mangas` is the path to the txt file containing a list of urls of the manga from any of the supported websites. Please see `manga.example.txt` for an example of what is required.

`multi_threaded` this enables mulit threaded chapter donwloads, the number of chapters downloaded at once is defined by `num_threads`

`save_location` Location of where the mangas are saved to once downloaded
