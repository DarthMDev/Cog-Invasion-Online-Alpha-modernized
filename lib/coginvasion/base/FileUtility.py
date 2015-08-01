"""

  Filename: FileUtility.py
  Created by: blach (18Apr15)

"""

from panda3d.core import VirtualFileSystem, Filename

def findAllModelFilesInVFS(phase_array):
	models = []
	vfs = VirtualFileSystem.getGlobalPtr()
	for phase in phase_array:
		fileList = vfs.scanDirectory(Filename(phase))
		for fileName in fileList:
			if (fileName.get_filename().get_fullpath().endswith(".bam") or
			fileName.get_filename().get_fullpath().endswith(".egg") or
			fileName.get_filename().get_fullpath().endswith(".pz")):
				if not fileName.get_filename().get_fullpath() in models:
					models.append(fileName.get_filename().get_fullpath())
			else:
				# it must be a folder, scan that folder for files
				fileList2 = vfs.scanDirectory(Filename(fileName.get_filename().get_fullpath()))
				for fileName2 in fileList2:
					if (fileName2.get_filename().get_fullpath().endswith(".bam") or
					fileName2.get_filename().get_fullpath().endswith(".egg") or
					fileName2.get_filename().get_fullpath().endswith(".pz")):
						if not fileName2.get_filename().get_fullpath() in models:
							models.append(fileName2.get_filename().get_fullpath())
	return models
