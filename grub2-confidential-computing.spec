%global _enable_debug_packages 0

%ifarch aarch64
%global grub_arch arm64-efi
%endif
%ifarch x86_64
%global grub_arch x86_64-efi
%endif
%global grub_dir /usr/lib/grub/%{grub_arch}

%global grub_epoch %{expand:%%(\\\
	rpm -q grub2-efi-%{efi_arch} | rpmsort | tail -1 \\\
	| xargs -r rpm -q --qf '%{epoch}')}
%global grub_version %{expand:%%(\\\
	rpm -q grub2-efi-%{efi_arch} | rpmsort | tail -1 \\\
	| xargs -r rpm -q --qf '%{version}')}
%global grub_release %{expand:%%(\\\
	rpm -q grub2-efi-%{efi_arch} | rpmsort | tail -1 \\\
	| xargs -r rpm -q --qf '%{release}')}

Name:		grub2-confidential-computing
Epoch:		%{grub_epoch}
Version:	%{grub_version}
Release:	%{grub_release}
Summary:	Grub image for use in confidential computing
License:	GPL-3.0-or-later
URL:		http://www.gnu.org/software/grub/

ExclusiveArch:	aarch64 x86_64

BuildRequires:	coreutils
BuildRequires:	efi-srpm-macros
BuildRequires:	findutils
BuildRequires:	grub2-efi-%{efi_arch}
BuildRequires:	grub2-efi-%{efi_arch}-modules
BuildRequires:	grub2-tools
BuildRequires:	pesign
BuildRequires:	rpm
BuildRequires:	sed
BuildRequires:	squashfs-tools

Source0:	grub.cfg
Source1:	sbat.csv.in
Source2:	grubenv

%description
This is a grub image for use in confidential computing VMs.

%prep
%autosetup -S git -T -c

%build
mkdir -p memdisk/fonts
cp /usr/share/grub/unicode.pf2 memdisk/fonts
mksquashfs memdisk memdisk.squashfs -comp lzo

sed \
	-e 's,@@VERSION@@,%{grub_version},g' \
	-e 's,@@VERSION_RELEASE@@,%{grub_version}-%{grub_release},g' \
	< '%{SOURCE1}' > sbat.csv

grub2-mkimage \
	-O %{grub_arch} \
	-o grub%{efi_arch}.efi.orig \
	-m memdisk.squashfs \
	-c '%{SOURCE0}' \
	-p /EFI/%{efi_vendor} \
	--sbat sbat.csv \
	-d '%{grub_dir}' \
	all_video at_keyboard \
	backtrace blscfg boot \
	cat chain configfile connectefi cryptodisk \
	echo efi_netfs efifwsetup efinet ext2 \
	f2fs fat font \
	gcry_rijndael gcry_rsa gcry_serpent gcry_sha256 gcry_twofish \
	gcry_whirlpool gfxmenu gfxterm gzio \
	halt http \
	increment iso9660 \
	jpeg \
	keylayouts \
	linux loadenv loopback lsefi lsefimmap luks luks2 lvm \
	mdraid09 mdraid1x minicmd \
	net normal \
	part_apple part_msdos part_gpt password_pbkdf2 pgp png \
	reboot regexp \
	search search_fs_uuid search_fs_file search_label serial sleep \
	syslinuxcfg \
	test tftp tpm \
	usb usbserial_common usbserial_pl2303 usbserial_ftdi \
	usbserial_usbdebug \
	version video \
	xfs \
	zstd

%pesign -s -i grub%{efi_arch}.efi.orig -o grub%{efi_arch}.efi

%install
set -e
install -d -m 0700 ${RPM_BUILD_ROOT}'%{_libdir}/%{name}/'
install -m 0644 grub%{efi_arch}.efi \
	${RPM_BUILD_ROOT}'%{_libdir}/%{name}/grub%{efi_arch}.efi'
install -d -m 0700 ${RPM_BUILD_ROOT}%{efi_esp_dir}
# grubenv is o+rwx because of filesystem limitations
install -m 0700 %{SOURCE2} ${RPM_BUILD_ROOT}%{efi_esp_dir}

%files
%attr(0700,root,root) %dir %{_libdir}/%{name}
%attr(0644,root,root) %{_libdir}/%{name}/*
%attr(0700,root,root) %dir %{efi_esp_dir}
# grubenv is o+rwx because of filesystem limitations
%ghost %config(noreplace) %verify(not mtime) %attr(0700,root,root)%{efi_esp_dir}/grubenv

%changelog
* Wed Nov 19 2025 Peter Jones <pjones@redhat.com> - 1-1
- Sigh.
