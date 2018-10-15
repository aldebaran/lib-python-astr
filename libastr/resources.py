#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""libastr objects to simplify interfaces.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import json
import os.path
import zipfile
import shutil

from libastr.client import AstrClient
from .logger import get_logger
from .exceptions import *

MAX_FILE_NUMBER = 50


# - [ Browser ] --------------------------------------------------------------

class Browser(object):
    """Class to search for items in ASTR."""

    def __init__(self, astrclient=None):
        """Initialize a Browser class with an AstrClient instance.

        Args:
            astrclient (AstrClient): (optional) A AstrClient instance to
                communicate with the ASTR server. If no parameter is given
                a new AstrClient instance will be created.
        """
        if astrclient is None:
            astrclient = AstrClient()
        self._astrclient = astrclient

    # -----------------------------------------
    # Methods for archives
    # -----------------------------------------

    def _json_to_archive(self, json_object):
        """Convert the API object into an Archive object.

        Args:
            json_object: json object returned by ASTR API

        Returns:
            (Archive) associated archive

        """
        descriptors = {}
        for descriptor in json_object["descriptors"]:
            descriptors[descriptor["name"]] = descriptor["value"]
        if "comments" in json_object:
            return Archive(id_=json_object["_id"],
                           author=json_object["author"],
                           date=json_object["date"],
                           category=json_object["category"],
                           comments=json_object["comments"],
                           descriptors=descriptors,
                           astrclient=self._astrclient)
        else:
            return Archive(id_=json_object["_id"],
                           author=json_object["author"],
                           date=json_object["date"],
                           category=json_object["category"],
                           descriptors=descriptors,
                           astrclient=self._astrclient)

    def _json_to_list_of_archives(self, json_list):
        """Convert the API array into a list of Archives.

        Args:
            json_list: json array returned by ASTR API

        Returns:
            (List[Archive]) associated list of archives

        """
        archives_list = []
        for json_archive in json_list:
            archives_list.append(self._json_to_archive(json_archive))
        return archives_list

    def get_all_archives(self):
        """Get all archives.

        Returns:
            (List[Archive]) list of all archives

        """
        return self._json_to_list_of_archives(self._astrclient.send_get("archives"))

    def get_archive_by_id(self, id_):
        """Get the archive with the associated id.

        Args:
            id_ (str): archive id (e.g. 5b29162874f5a43fc26f1f34)

        Returns:
            (Archive) associated archive

        """
        return self._json_to_archive(self._astrclient.send_get("archives/id/" + id_))

    def get_archives_by_mongodb_query(self, query):
        """Get the archives that match with the mongoDB query.

        Args:
            query: mongoDB query (e.g. {category: "MY_CAT", author: "John DOE"})

        Returns:
            (List[Archive]) list of archives

        """
        return self._json_to_list_of_archives(self._astrclient.send_post("archives", params=query))

    def get_archives_by_args(self, author=None, date=None, category=None, descriptors=None):
        """Get the archives that match with the arguments.

        Args:
            author: (optional) archive author (e.g. John DOE)
            date: (optional) archive date or range of dates
                  (e.g. "2018-05-30" or ["2018-05-30", "2018-06-15"])
            category: (optional) archive category (e.g. MY_CATEGORY)
            descriptors: (optional) dictionary of descriptors
                         (e.g. {"my_desc": "MY VALUE"})

        Returns:
            (List[Archive]) list of archives

        """
        query = {}
        if author is not None:
            query["author"] = author
        if date is not None:
            query["date"] = date
        if category is not None:
            query["category"] = category
        if descriptors is not None:
            descriptors_list = []
            for key, value in descriptors.items():
                descriptors_list.append({
                    "descriptors": {
                        "$elemMatch": {
                            "name": key,
                            "value": value
                        }
                    }
                })
            query["$and"] = descriptors_list
        return self.get_archives_by_mongodb_query(query)

    # -----------------------------------------
    # Methods for archive categories
    # -----------------------------------------

    def _json_to_archive_category(self, json_object):
        """Convert the API object into a ArchiveCategory object.

        Args:
            json_object: json object returned by ASTR API

        Returns:
            (ArchiveCategory) associated archive category

        """
        descriptors = {}
        for descriptor in json_object["descriptors"]:
            descriptors[descriptor["name"]] = descriptor["options"]
        return ArchiveCategory(id_=json_object["_id"],
                               name=json_object["name"],
                               author=json_object["author"],
                               descriptors=descriptors,
                               astrclient=self._astrclient)

    def _json_to_list_of_archive_categories(self, json_list):
        """Convert the API array into a list of ArchiveCategory.

        Args:
            json_list: json array returned by ASTR API

        Returns:
            (List[ArchiveCategory]) associated list of archive categories

        """
        archive_categories_list = []
        for json_object in json_list:
            archive_categories_list.append(self._json_to_archive_category(json_object))
        return archive_categories_list

    def get_all_descriptors(self):
        """Get all existing descriptors of all archive categories.

           Only categories that were used at least one time are concerned.

        Returns:
            (List) all descriptors

        """
        return self._astrclient.send_get("archives/descriptors")

    def get_all_archive_categories(self):
        """Get all archive categories.

        Returns:
            (List[ArchiveCategory]) list of all archive categories

        """
        return self._json_to_list_of_archive_categories(self._astrclient.send_get("categories"))

    def get_archive_category_by_id(self, id_):
        """Get the archive category with the associated id.

        Args:
            id_: archive category id (e.g. 5aeb2225b5a8a90b8affc162)

        Returns:
            (ArchiveCategory) associated archive category

        """
        return self._json_to_archive_category(self._astrclient.send_get("categories/id/" + id_))

    def get_archive_category_by_name(self, name):
        """Get the archive category with the associated name.

        Args:
            name: archive category name (e.g. MY_CAT)

        Returns:
            (ArchiveCategory) associated archive category

        """
        return self._json_to_archive_category(self._astrclient.send_get("categories/name/" + name))


# - [ Archive ] --------------------------------------------------------------

class Archive(object):
    """Class representing an archive from ASTR."""

    def __init__(self, date, category, descriptors, author=None,
                 comments=None, id_=None, astrclient=None):
        """Create a new archive from scratch.

        User should directly instantiate this class only in the case he
        wants to create a new archive which does not exist on ASTR server.
        To retrieve an existing archive from ASTR, user should use
        Browser.get_archive_by_id() instead.

        Args:
            date (str): Date in the format YYYY-MM-DD
            category (str): Name of the archive category.
                It must already exist on ASTR server.
            descriptors (dict): Dictionary of descriptors. All descriptors
                of the category must be present and not null. To get the
                the list of descriptors, use ArchiveCategory.get_descriptors()
            author (str): (optional) Useless if archive is created from scratch.
                User defined in the AstrClient instance will be used.
            comments (str): (optional) Comments about this archive.
            id_ (str): (optional) Useless if archive is created from scratch.
                A unique ID will be given by the ASTR server during the upload.
            astrclient (AstrClient): (optional) An instance of AstrClient
                to communicate with the ASTR server.

        Attributes:
            id_ (string): The id of the archive. Valid only if the archive has been
              retrieved from the server.
            date (string): The given date of the archive.
            category (string): The category of the archive.
            author (string): The author of the archive.
            comments (string): The comments of the archive.
            descriptors (dict): Dictionary of descriptors and their values.
        """
        self._logger = get_logger(self.__class__.__name__)
        self.id_ = id_
        self.date = date
        self.category = category
        self.author = author
        self.comments = comments
        self.descriptors = descriptors
        self._astrclient = astrclient if astrclient else AstrClient()
        self._astr_items = {'id_': self.id_,
                            'date': self.date,
                            'category': self.category,
                            'author': self.author,
                            'comments': self.comments,
                            'descriptors': self.descriptors}

    def __repr__(self):
        return "<{}.{}, id={}>\n{}".format(__name__,
                                           self.__class__.__name__,
                                           id(self),
                                           json.dumps(self._astr_items,
                                                      sort_keys=True,
                                                      indent=4))

    def _object_to_dict(self):
        """Create a dict with only useful data from this archive.

        Returns:
            (dict) Dictionary containing useful data from this archive

        """
        data = self._astr_items
        descriptors = []
        for key, value in self.descriptors.items():
            descriptors.append({"name": key, "value": value})
        data["descriptors"] = descriptors
        return data

    def delete(self):
        """Delete this archive from ASTR.

        Raises:
            Same than AstrClient.send_delete()
        """
        self._astrclient.send_delete("archives/id/" + self.id_)

    def update(self, date=None, comments=None, descriptors=None):
        """Update info about this archive on ASTR.

        Args:
            date: (optional) archive date (e.g. 2018-05-30)
            comments: (optional) comments about the archive
            descriptors: (optional) dictionary of descriptors
                         (e.g. {"my_desc": "MY VALUE", "my_second_desc": "VAL"})
                         only the values of existing descriptors can be modified

        Raises:
            Same than AstrClient.send_post()
        """
        body_request = {}
        if date is not None:
            body_request["date"] = date
        if comments is not None:
            body_request["comments"] = comments
        if descriptors is not None:
            descriptors_list = []
            for key, value in descriptors.items():
                descriptors_list.append({"name": key, "value": value})
            body_request["descriptors"] = descriptors_list
        self._astrclient.send_post("archives/id/" + self.id_,
                                   params=body_request)

    def upload(self, file_paths):
        """Upload this archive to ASTR.

        Args:
            file_paths: list of all the files to upload in the zip
                   (e.g. ["/home/john.doe/Desktop/file_1.txt",
                          "/home/john.doe/Desktop/file_2.png"])

        Raises:
            PathError: if the given file paths are not valid.
            ArchiveError: if an error occured while adding the new archive
              to the ASTR database.
            Other exceptions: same than AstrClient.upload()
        """
        filenames = []
        if len(file_paths) == 0:
            raise PathError("Empty list of paths.")
        elif len(file_paths) > MAX_FILE_NUMBER:
            raise PathError("Too many files to upload ({}). The limit is {}."
                            .format(len(file_paths), MAX_FILE_NUMBER))
        for path in file_paths:
            if not os.path.isfile(path):
                raise PathError("{} is not a file".format(path))
            elif os.path.basename(path) in filenames:
                raise PathError("Cannot upload 2 files with",
                                "the same name: {}".format(
                                    os.path.basename(path)))
            else:
                filenames.append(os.path.basename(path))

        data = self._object_to_dict()
        data['author'] = self._astrclient.get_username()
        res = self._astrclient.send_post("archives/add", params=data)
        if res["name"] == "Failed":
            raise ArchiveError(res)
        else:
            archive_id = res['archive']['_id']
            self._astrclient.upload(uri="upload",
                                    paths=file_paths,
                                    zip_name=archive_id)
            self.id_ = archive_id

    def replace_zip(self, file_paths):
        """Replace the zip file of this archive with a new one.

        Args:
            file_paths: list of all the files to upload in the zip
               (e.g. ["/home/john.doe/Desktop/file_1.txt",
                      "/home/john.doe/Desktop/file_2.png"])

        Raises:
            PathError: if given file paths are not valid.
            Other exceptions: Same than AstrClient.upload()
        """
        filenames = []
        if len(file_paths) == 0:
            raise PathError("Empty list of paths.")
        elif len(file_paths) > MAX_FILE_NUMBER:
            raise PathError("Too many files to upload ({}). The limit is {}."
                            .format(len(file_paths), MAX_FILE_NUMBER))
        for path in file_paths:
            if not os.path.isfile(path):
                raise PathError("{} is not a file".format(path))
            elif os.path.basename(path) in filenames:
                raise PathError("Cannot upload 2 files with the same name: {}"
                                .format(os.path.basename(path)))
            else:
                filenames.append(os.path.basename(path))
        # update archive (last modification date)
        self._astrclient.send_post("archives/id/" + self.id_,
                                   params={"newArchive": "true"})
        # upload new files
        self._astrclient.upload(uri="upload/replace-zip",
                                paths=file_paths,
                                zip_name=self.id_)


    def download(self, local_path, extract=False):
        """Download the archive to a local directory.

        Args:
            local_path: local directory where the zip will be downloaded
                  (e.g. "/home/john.doe/Desktop")
            extract: (bool) (optional) If True, the downloaded archive will immediately
              be decompressed and extracted. Contents of the archive will be located in
              a subdirectory of the given local path, named with the unique ID
              of the archive. If this subdirectory already exists, it will be overwritten.

        Raises:
             PathError: if the given local path is not valid.
             Exception: if an issue occured during download.
             Other exceptions: same than AstrClient.download()
        """
        if not os.path.isdir(local_path):
            raise PathError("{} is not a valid directory".format(local_path))
        path_to_zip = os.path.join(local_path, self.id_ + '.zip')
        self._astrclient.download(uri="download/id/" + self.id_, path=path_to_zip)
        
        if extract:
            archive_folder = os.path.join(local_path, self.id_)
            # If the folder to extract files already exists, remove it and its content.
            if os.path.isdir(archive_folder):
                shutil.rmtree(archive_folder)
            # Create a new folder for this archive
            os.mkdir(archive_folder)
            # Extract the zip file
            zip_ref = zipfile.ZipFile(path_to_zip, 'r')
            zip_ref.extractall(archive_folder)
            zip_ref.close()
            # Remove the useless .zip file
            os.remove(path_to_zip)
        

# - [ Archive Category ] ----------------------------------------------------

class ArchiveCategory(object):
    """Class representing an archive category from ASTR."""

    def __init__(self, id_, name, author, descriptors, astrclient=None):
        self._logger = get_logger(self.__class__.__name__)
        self.id_ = id_
        self.name = name
        self.author = author
        self.descriptors = descriptors
        self._astrclient = astrclient if astrclient else AstrClient()
        self._astr_items = {'id_': self.id_,
                            'name': self.name,
                            'author': self.author,
                            'descriptors': self.descriptors}

    def __repr__(self):
        return "<{}.{}, id={}>\n{}".format(__name__,
                                           self.__class__.__name__,
                                           id(self),
                                           json.dumps(self._astr_items,
                                                      sort_keys=True,
                                                      indent=4))

    def get_descriptors(self):
        """Get the descriptors of a this category.

        Returns:
            (List) descriptors of this category

        """
        return self._astrclient.send_get("archives/descriptors/" + self.name)

    def get_descriptor_options(self, descriptor_name):
        """Get the options of a descriptor.

        Args:
            descriptor_name(str): descriptor name (e.g. my_desc)

        Returns:
            (List) list of options of the descriptor
                (e.g. ["OPTION 1", "OPTION 2", ...])

        """
        return self._astrclient.send_get("categories/options/{}/{}".format(
            self.name, descriptor_name))
