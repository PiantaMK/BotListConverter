# BotListConverter 
Script that converts some online BotLists into a valid Lmaobox playerlist/lua.

---

# List of supported databases:
- d3fc0n6's:
    - Bot list
    - Cheater list
    - Tacobot list
    - Pazer list
- [bots.tf](https://bots.tf/) database
- megascatterbomb's Mega Cheater Database

# How to use:
1. Make sure python is installed. You can get it at https://www.python.org/downloads/. Make sure you add it to the PATH too, or else it'll be more difficult to use.
2. Download the source and open a command prompt or powershell window where you opened it. This can be done in the File Explorer by pressing `File -> Open Windows Powershell`.
3. Install the requirements. `python -m pip install -r requirements.txt` or double-click the `install_requirements.bat` file.
3. Run the script in the prompt you just opened. ```python .\main.py --help``` will display information on how to use it.
4. Once you finish using it, import the newly exported playerlist into Nullcore.

# Example:
### To export a list of bots into a lua:
```powershell
python .\main.py -l bot -f lua
```
### To export a list of cheaters into a playerlist
```powershell
python .\main.py -l cheater -f amalgam
```
---
# Credits
- [Leadscales](https://github.com/leadscales) - for making the [original version](https://github.com/leadscales/PazerListNCC)
- [Surepy/sleepy](https://github.com/surepy) - for the [base](https://github.com/surepy/tf2db-sleepy-list/blob/main/export_megacheaterdb_as_tf2bd.py) for the [MCDB parser]([https://github.com/surepy/tf2db-sleepy-list/blob/main/export_megacheaterdb_as_tf2bd.py](https://github.com/PiantaMK/BotListConverter/blob/main/src/parser/megadb.py))
