# bdist_debian.py
#
# Add 'bdist_debian' Debian binary package distribution support to 'distutils'.
#
# Written by: Gene Cash <gene.cash@gmail.com> 16-NOV-2007
# Extended by: Chris Freeze <cfreeze@users.sourceforge.net> 11/08/2008
#       * Removed Nokia specific items
#       * Added other keywords that can be in the control file

import os, base64

from distutils.core import Command, Distribution
from distutils.dir_util import remove_tree
from distutils.util import byte_compile


# Make these legal keywords for setup()
Distribution.icon = ""
Distribution.section = ""
Distribution.depends = ""
Distribution.recommends = ""
Distribution.suggests = ""
Distribution.architecture = ""
Distribution.essential = ""
Distribution.source = ""

class ControlFile(object):
    def __init__(self, Installed_Size=0, Long_Description='', Description='', Icon='', **kwargs):
        self.options=kwargs
        self.description=Description
        self.long_description=Long_Description
        self.icon=Icon
        self.installed_size=Installed_Size

    def getContent(self):
        content = ['%s: %s' % (k, v) for k,v in self.options.iteritems()]

        content.append('Installed-Size: %d' % self.installed_size)
        if self.description != 'UNKNOWN':
            content.append('Description: %s' % self.description.strip())
            if self.long_description != 'UNKNOWN':
                self.long_description = self.long_description.replace('\n', '\n ')
                content.append(" %s" % self.long_description.strip())

        if self.icon:

            # Generate Base64-encoded icon
            s = file(self.icon, 'rb').read()
            x = base64.b64encode(s)

            # Wrap width MUST be 76 characters to make application manager happy after install
            lw = 76

            # Trailing blank is important
            content.append('XB-Maemo-Icon-26: ')
            for i in range(0, len(x), lw):
                content.append(" %s" % x[i:i +lw])

        # Must have two NEW_LINE
        return '\n'.join(content) + "\n\n"

class bdist_debian(Command):
    description = ""

    # List of option tuples: long name, short name (None if no short name), and help string.
    user_options=[('name=', None, 'Package name'),
                  ('section=', None, 'Section (Only "user/*" will display in App Mgr usually) (default=user/other)'),
                  ('priority=', None, 'Priority  (default=optional)'),
                  ('depends=', None, 'Other Debian package dependencies (comma separated) (default=python)'),
                  ('recommends=', None, 'Other Debian package you recommend (comma separated) (default=none)'),
                  ('suggests=', None, 'Other Debian package you suggest (comma separated) (default=none)'),
                  ('essential=', None, 'Whether packge is essential(yes/no) (default=no)'),
                  ('architecture=', None, 'Target architecture (default=all)'),
                  ('source=', None, 'Source keyword.. (default=package_name)'),
                  ('icon=', None, 'Name of icon file to be displayed by App Mgr')]

    def initialize_options(self):
        self.section = None
        self.priority = None
        self.depends = None
        self.recommends = None
        self.suggests = None
        self.architecture = None
        self.essential = None
        self.source = None
        self.icon = None

    def finalize_options(self):
        if self.section is None:
            self.section='user/other'

        if self.priority is None:
            self.priority='optional'

        self.maintainer='%s <%s>' % (self.distribution.get_maintainer(), self.distribution.get_maintainer_email())

        if self.depends is None:
            self.depends='python'

        self.name = self.distribution.get_name()
        self.description = self.distribution.get_description()
        self.long_description = self.distribution.get_long_description()
        self.version = self.distribution.get_version()

        if self.source is None:
            self.source = self.name

        # Process new keywords
        if self.distribution.icon is not None:
            self.icon = self.distribution.icon
        if self.distribution.section is not None:
            self.section = self.distribution.section
        if self.distribution.depends is not None:
            self.depends = self.distribution.depends
        if self.distribution.recommends is not None:
            self.recommends = self.distribution.recommends
        if self.distribution.suggests is not None:
            self.suggests = self.distribution.suggests
        if self.distribution.architecture is not None:
            self.architecture = self.distribution.architecture
        if self.distribution.essential is not None:
            self.essential = self.distribution.essential

    def run(self):
        build_dir=os.path.join(self.get_finalized_command('build').build_base, 'debian')
        dist_dir='dist'
        binary_fn='debian-binary'
        control_fn='control'
        data_fn='data'
        tgz_ext='.tar.gz'

        # build everything locally
        self.run_command('build')
        install=self.reinitialize_command('install', reinit_subcommands=1)
        install.root=build_dir
        self.run_command('install')

        # find out how much space it takes
        installed_size=0
        for root, dirs, files in os.walk('build'):
            installed_size += sum(os.path.getsize(os.path.join(root, name)) for name in files)

        # make compressed tarball
        self.make_archive(os.path.join(dist_dir, data_fn), 'gztar', root_dir=build_dir)

        # remove all the stuff we just built
        remove_tree(build_dir)

        # create control file contents
        ctl = ControlFile(Package=self.name,
                          Version=self.version,
                          Section=self.section,
                          Priority=self.priority,
                          Installed_Size=installed_size / 1024 + 1,
                          Architecture=self.architecture,
                          Maintainer=self.maintainer,
                          Depends=self.depends,
                          Description=self.description,
                          Long_Description=self.long_description,
                          Recommends=self.recommends,
                          Suggests=self.suggests,
                          Essential=self.essential,
                          Source=self.source,
                          Icon=self.icon).getContent()

        # grab scripts
        scripts={}
        for fn in ('postinst', 'preinst', 'postrm', 'prerm', 'config'):
            if os.path.exists(fn):
                scripts[fn]=file(fn, 'rb').read()

        # now to create the deb package
        os.chdir(dist_dir)

        # write control file
        file(control_fn, 'wb').write(ctl)

        # write any scripts and chmod a+rx them
        files=[control_fn]
        for fn in scripts:
            files.append(fn)
            file(fn, 'wb').write(scripts[fn])
            os.chmod(fn, 0555)

        # make "control" compressed tarball with control file and any scripts
        self.spawn(['tar', '-czf', control_fn+tgz_ext]+files)

        # make debian-binary file
        file(binary_fn, 'wb').write('2.0\n')

        # make final archive
        package_filename='%s_%s_all.deb' % (self.name, self.version)
        self.spawn(['ar', '-cr', package_filename, binary_fn, control_fn+tgz_ext, data_fn+tgz_ext])

		# Remove unneeded files
        os.remove(control_fn)
        os.remove(control_fn+tgz_ext)
        os.remove(data_fn+tgz_ext)
        os.remove(binary_fn)
