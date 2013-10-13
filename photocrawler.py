#!/usr/bin/python
import sys, os, time

DOCUMENT_ROOT = '/media/WesternDigital/PhotoCrawler/files' # w/o tail slash
FILETYPES = ['.jpg', '.jpeg', '.png']
SKIP_HIDDEN_DIRS = True # Skip dirs starting with a dot
SIZE_CUTOFF = 10240 #bytes (smaller files are ignored)


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
		
	def findPhotos(self, top='/'):
		content = os.listdir(top)
		dirs = []
		files = []
		for element in content:
			path = os.path.join(top, element)
			if os.path.isdir(path):
				dirs.append(path)
			elif os.path.isfile(path):
				files.append(path)
		for name in files:
			if os.path.getsize(name) < SIZE_CUTOFF:
				continue
			ext = os.path.splitext(name)[-1].lower()
			if ext in FILETYPES:
				md5 = os.popen('md5sum "%s"' % name).read()
				md5 = md5.split(' ')[0]
				self.new_hashes.append(md5)
				self.new_files.append(name)
		for d in dirs:
			if d == self.document_root:
				continue
			if SKIP_HIDDEN_DIRS:
				if os.path.split(d)[-1][0] == '.':
					continue
			self.findPhotos(d)
		
	def loadHashList(self, filename=None):
		if not filename:
			p = '/'.join(self.document_root[:-1].split('/')[:-1])
			filename = os.path.join(p, 'hash_values.md5')
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
			filename = os.path.join(self.document_root, '../hash_values.md5')
		f = open(filename, 'a')
		f.write(h+' '+p+'\n')
		f.close()
	
	def compareHashValues(self):
		for i in range(len(self.new_files)):
			h = self.new_hashes[i]
			f = self.new_files[i]
			if h in self.hash_list:
				#print 'Photo already copied, trying to make symbolic link...')
				self.linkFile(f, h)
			else:
				dest = self.document_root + f
				os.popen('mkdir -p "%s"' % os.path.dirname(dest))
				self.copyFile(f, dest)
				self.appendHash(h, f)
				self.hash_list.append(h)
				self.files_list.append(f)
	
	def linkFile(self, f, h):
		dest = self.document_root + f
		if os.path.exists(dest):
			return
		i = self.hash_list.index(h)
		p = self.files_list[i]
		p = (f.count('/')-1)*'../' + p[1:]
		os.popen('mkdir -p "%s"' % os.path.dirname(dest))
		os.popen('ln -s "%s" "%s"' % (p, dest))
		#print 'ln -s "%s" "%s"' % (p, dest)
	
	def copyFile(self, src, dest):
		#print 'Copying "%s" to "%s"...' % (src, dest)
		if os.path.exists(dest):
			#print 'File exists, renaming...'	
			t = dest.split('/')[-1].split('_')
			#print t	
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
			#print 'cp -p "%s" "%s"' % (src, dest)
			#print 'Comparing original to copy to validate copy...'
			p = os.popen('cmp "%s" "%s" 2>&1' % (src, dest))
			r = p.read()
			p.close()
			if len(r):
				sys.stderr.write('ERROR: Error in copying file "%s" to location "%s". The hash keys does not match.\n' % (src, dest))
				sys.exit(-1)
			
			
	
	
	
	
if __name__ == '__main__':
	
	p = PhotoCrawler()
	p.setDocumentRoot(DOCUMENT_ROOT)
	
	print 'Reading hash list...'
	t0 = time.time()
	p.loadHashList()
	t1 = time.time()
	print t1-t0, 'secs'
	print 'Crawling for photos...'
	p.findPhotos(sys.argv[1])
	t2 = time.time()
	print t2-t1, 'secs'
	print 'Comparing hash values and copying files...'
	p.compareHashValues()
	t3 = time.time()
	print t3-t2, 'secs'
	print 'Done in %f sec' % (t3-t0)
	
todo = """

- Add some sort of feedback to see what the program does.
- Add some way of configuring the program i.e. arguments or conf file.
- Make an option to exclude certain directories
- Make the program run parallel. (One process for finding, one for hash checking
	and one for file transfer.


"""

	
	
