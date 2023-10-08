import os
import shutil
from os.path import splitext, exists, join
from shutil import move
from time import sleep
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Diretórios fonte e destino
source_dir = os.path.expanduser("~/Downloads")
dest_dir_books = os.path.expanduser("~/Downloads/livros")
dest_dir_documents = os.path.expanduser("~/Downloads/documentos")

# Extensões de documentos
document_extensions = [".doc", ".docx", ".odt", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]

def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name

def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        try:
            rename(oldName, newName)
            logging.info(f"Renamed existing file: {name} to {unique_name}")
        except Exception as e:
            logging.error(f"Error renaming file {name}: {e}")
    try:
        move(entry, dest)
        logging.info(f"Moved file: {name} to {dest}")
    except Exception as e:
        logging.error(f"Error moving file {name} to {dest}: {e}")

class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        with os.scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                self.check_document_files(entry, name)

    def check_document_files(self, entry, name):  
        for document_extension in document_extensions:
            if name.endswith(document_extension) or name.endswith(document_extension.upper()):
                move_file(dest_dir_documents, entry, name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
