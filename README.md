# Slack corpus generator

### Usage

* Install the dependencies with `pip3 install -r requirements.txt`
* Invoke the program with `python3 corpus.py` in order to create a file called [`corpus.json`](/corpus.json)

**Note: the API requsts are being cached internally; to repeat them you must delete the dotfiles inside [`cache`](/cache)**

### Pending tasks

* Improve the quality of the used algorithms and/or the [`skills.txt`](/skills.txt) file (extracted from [tool-experience-tagger](https://github.com/helpfulengineering/tool-experience-tagger/blob/master/sample-data/skills_processed.txt))
