from __future__ import annotations
# Use annotations here to keep the type suggestions without causing a circular import

import Watcher

class Servers():
    """
    Static class that contains a dict of all Watchers and what guilds they are associated with.

    Because this class is static it is accessible without any variables yet still persists data.

    ...

    Methods
    -------
    add(server: `int`, watcher: `Watcher`):
        Registers a Watcher to the provided guild id.
    get_watcher(server: `int`):
        Get the Watcher associated with the provided guild id, if any.
    set_watcher(server: `int`, watcher: `Watcher`):
        Replaces/registers a Watcher to the provided guild id.
    remove(server: `int` | `Watcher`):
        Unregisters a Watcher by guild id or Object.
    """
    dict = {}

    @staticmethod
    def add(server: int, watcher: Watcher.Watcher) -> None:
        """
        Registers a Watcher to the provided guild id.
        
        Parameters
        ----------
        server : `int`
            The guild ID to associate the Watcher with.
        watcher : `Watcher`
            The watcher to be associated with the guild ID.
        """
        Servers.dict[server] = watcher

    @staticmethod
    def get_watcher(server: int) -> Watcher.Watcher:
        """
        Get the Watcher associated with the provided guild id, if any.

        Parameters
        ----------
        server: `int`
            The guild id to search for a Watcher under.

        Return
        ------
        `Watcher`:
            The Watcher associated with the guild.
        `None`:
            Returned if there is no Watcher associated with the guild id.
        """
        return Servers.dict.get(server)

    @staticmethod
    def set_watcher(server: int, watcher: Watcher.Watcher) -> None:
        """
        Replaces/registers a Watcher to the provided guild id.        

        Parameters
        ----------
        server : `int`
            The guild ID to associate the Watcher with.
        watcher : `Watcher`
            The watcher to be associated with the guild ID.
        """
        Servers.dict.update({server : watcher})

    @staticmethod
    def remove(server: Watcher.Watcher | int) -> None:
        """
        Unregisters a Watcher by guild id or Object.

        Parameters
        ----------
        server : `int` | `Watcher`
            The id of the guild associated with the Watcher or the Watcher itself.

        Raises
        ------
        `IndexError`
            If the id or Watcher were not found within the dict.

        """
        #TODO find a faster method than this for removing by Watcher
        #O(n) in the worst case. (I think?)
        if isinstance(server, Watcher.Watcher):
            for key, value in Servers.dict.items():
                if value == server:
                    del Servers.dict[key]
                    return
            raise IndexError("Something went wrong, attempted to delete nonexistent Watcher.")
        del Servers.dict[str(server)]