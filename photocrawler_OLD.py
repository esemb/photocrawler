#!/usr/bin/python
import sys, os, time

class PhotoCrawler:
	def __init__(self):
		self.document_root = None # path to photo storage
		self.hash_list = []  # list of all previously known hash values
		self.files_list = [] # list of all previously known files
		self.files_to_copy = []   # list of all the photos to copy
		self.new_hashes = [] # hash values of found photos
		self.new_files = []  # paths to found photos
	
	def setDocumentRoot(self, path=None):
		self.document_root = path

	def findPhotos(self):		
		#cmd = """find -P /home -path */PhotoCrawler -prune -o \( \( -iname \*.png -size +100 \) -o -iname \*.jpg \) -type f -exec md5sum '{}' \; 2>/dev/null"""
		
		cmd = """find / -path */PhotoCrawler -prune -o \( \( -iname \*.png -size +100 \) -o -iname \*.jpg \) -type f -exec md5sum '{}' \; 2>/dev/null"""
		
		pipe = os.popen(cmd)
		lines = pipe.readlines()
			
		for line in lines:
			f = line.split(' ')
			try:
				self.new_hashes.append(f[0])
			except IndexError:
				continue
			try:
				self.new_files.append(' '.join(f[1:]).strip())
			except IndexError:
				self.new_hashes.pop()
		
	def loadHashList(self, filename=None):
		if not filename:
			filename = os.path.join(self.document_root, 'hash_values.md5')
		f = open(filename, 'r')
		lines = f.readlines()
		f.close()
		for line in lines:
			h = line.split(' ')[0]
			f = ' '.join(line.split(' ')[1:]).strip()
			self.hash_list.append(h)
			self.files_list.append(f)
	
	def appendHash(self, h, p, filename=None):
		if not filename:
			filename = os.path.join(self.document_root, 'hash_values.md5')
		f = open(filename, 'a')
		f.write(h+' '+p+'\n')
		f.close()
	
	def compareHashValues(self):
		for i in range(len(self.new_files)):
			h = self.new_hashes[i]
			f = self.new_files[i]
			if h in self.hash_list:
				print 'Photo already copied, trying to make symbolic link...'
				self.linkFile(f, h)
			else:
				self.files_to_copy.append((h, f))
	
	def linkFile(self, f, h):
		dest = self.document_root + f
		if os.path.exists(dest):
			return
		i = self.hash_list.index(h)
		p = self.files_list[i]
		os.popen('mkdir -p "%s"' % os.path.dirname(dest))
		os.popen('ln -s "%s" "%s"' % (p, dest))
		print 'ln -s "%s" "%s"' % (p, dest)
	
	def copyFile(self, src, dest):
		print 'Copying "%s" to "%s"...' % (src, dest)
		if os.path.exists(dest):
			print 'File exists, renaming...'	
			t = dest.split('/')[-1].split('_')
			print t	
			if len(t) > 1:
				if t[-1].isdigit():
					digit = int(t[-1]) + 1
					i = len(t[-1])
					self.copyFile(src, dest[:-i] + str(digit))
				else:
					self.copyFile(src, dest+'_2')
			else:
				self.copyFile(src, dest+'_2')
		else:
			os.popen('cp -p "%s" "%s"' % (src, dest)) # The copy command
			print 'cp -p "%s" "%s"' % (src, dest)
			print 'Comparing original to copy to validate copy...'
			p = os.popen('cmp "%s" "%s" 2>&1' % (src, dest))
			r = p.read()
			p.close()
			if len(r):
				sys.stderr.write('ERROR: Error in copying file "%s" to location "%s". The hash keys does not match.\n' % (src, dest))
				sys.exit(-1)
			
	def copyFiles(self):
		for h, f in self.files_to_copy:
			dest = self.document_root + f
			os.popen('mkdir -p "%s"' % os.path.dirname(dest))
			self.copyFile(f, dest)			
			self.appendHash(h, dest)
			
			
	
	
	
	
if __name__ == '__main__':
	t0 = time.time()
	p = PhotoCrawler()
	p.setDocumentRoot('/media/WesternDigital/PhotoCrawler') # w/o tail slash
	#p.setDocumentRoot('/home/ekj004/PhotoCrawler') # w/o tail slash
	print 'Reading hash list...'
	p.loadHashList()
	print 'Crawling for photos...'
	p.findPhotos()
	print 'Comparing hash values...'
	p.compareHashValues()
	print 'Copying files...'
	p.copyFiles()
	t = time.time()
	print 'Done in %d sec' % (t-t0)
	
todo = """

- Add some sort of feedback to see what the program does.
- Add some way of configuring the program i.e. arguments or conf file.
- Make an option to exclude certain directories
- Make the program run parallel. (One process for finding, one for hash checking
	and one for file transfer.


"""

	
	
