from pathlib import Path
import os

class Dir:
    def __init__(self, dirname):
        self.dirname = dirname
        self.files = []
        self.subdirs = []


    def build_dir(self):
        curr_dir = os.getcwd()

        new_path = os.path.join(curr_dir, self.dirname)
        os.chdir(new_path)
        
        p = Path(".")
        self.files = [str(f) for f in p.iterdir() if f.is_file()]
        subdirs  = [d for d in p.iterdir() if d.is_dir()]

        for subdir_name in subdirs:
            subdir = Dir(subdir_name)
            subdir.build_dir()
            self.subdirs.append(subdir)

        os.chdir("..") # backtrack


    def print_tree(self, tabs=0):
        print(tabs * " ", self.dirname)

        for subdir in self.subdirs:
            subdir.print_tree(tabs+1)


    def name_files(self):
        files = self.files.copy()
        print(files)

        for subdir in self.subdirs:
            files.extend(subdir.name_files())

        named_files = [str(self.dirname) + "/" + str(file_name) for file_name in files]

        return named_files


def main():
    dir_name = "test_dir"

    test_dir = Dir(dir_name)
    test_dir.build_dir()
    test_dir.print_tree()

    print(test_dir.name_files())


if __name__ == "__main__":
    main()
