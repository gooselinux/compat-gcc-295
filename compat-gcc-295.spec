%define _enable_debug_packages 0
%define debug_package %{nil}
Summary: GNU Compiler Collection for Red Hat Linux 7.1/s390x and 7.2/s390 compatibility
Name: compat-gcc-295
Epoch: 1
Version: 2.95.3
Release: 86%{?dist}
License: GPL
Group: Development/Languages
Source: gcc-2.95.3.tar.gz
Patch1: gcc-2.95.3-s390.patch
Patch2: gcc-2.95.3-s390-1.patch
Patch3: gcc-2.95.3-s390-2.patch
Patch4: gcc-2.95.3-s390-3.patch
Patch5: gcc-2.95.3-s390-4.patch
Patch6: gcc-2.95.3-s390-5.patch
Patch13: gcc-2.95.3-glibc224.patch
Patch14: gcc-2.95.3-libio.patch
Patch18: gcc-2.95.3-s390-undef.patch
Patch50: gcc-2.95.3-libgcc_s.patch
Patch51: gcc-2.95.3-s390x.patch
Patch52: gcc-2.95.3-libstdc++-libc-interface.patch
Patch53: gcc-2.95.3-udivwsdiv.patch
Patch54: gcc-2.95.3-s390x-compile.patch
URL: http://gcc.gnu.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch: s390 s390x

%define _gnu %{nil}

%description
This package is not created.

%package -n compat-libstdc++-295
Summary: Standard C++ libraries for Red Hat 7.1/s390x and 7.2/s390 backwards compatibility
Group: System Environment/Libraries
Requires: libgcc, libstdc++ >= 3.2
Obsoletes: compat-libstdc++
Epoch: 0

%description -n compat-libstdc++-295
The libstdc++ package contains a snapshot of the GCC Standard C++
Library v3, an ongoing project to implement the ISO 14882 Standard C++
library.

%package -n compat-libgcc-295
Summary: Compatibility 2.95.3 libgcc library
Group: Development/Languages
Obsoletes: gcc <= 2.96
Obsoletes: compat-gcc
Obsoletes: compat-gcc-legacy
Epoch: 0

%description -n compat-libgcc-295
The compat-libgcc-295 package contains 2.95.3 libgcc.a library and support
object files.

%prep
%setup -q -n gcc-2.95.3
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch13 -p1
%patch14 -p0
%patch18 -p1
%patch50 -p0
%patch51 -p0
%patch52 -p0
%ifarch s390
%patch53 -p0
%endif
%patch54 -p0

%build
%ifarch s390
# ssize_t used to be int in the very early days
echo '#ifndef _G_config_h' > libio/_G_config.h
echo '#include_next <_G_config.h>' >> libio/_G_config.h
echo '#undef _G_ssize_t' >> libio/_G_config.h
echo '#define _G_ssize_t int' >> libio/_G_config.h
echo '#endif' >> libio/_G_config.h
%endif
%ifarch s390x
# 2002-10-23 glibc changes made off64_t long long instead of long
echo '#ifndef _G_config_h' > libio/_G_config.h
echo '#include_next <_G_config.h>' >> libio/_G_config.h
echo '#undef _G_off64_t' >> libio/_G_config.h
echo 'typedef long int __gcc295_off64_t;' >> libio/_G_config.h
echo '#define _G_off64_t __gcc295_off64_t' >> libio/_G_config.h
echo '#endif' >> libio/_G_config.h
%endif
find . -name configure | xargs touch
touch gcc/cstamp-h.in
touch gcc/config.in

# Link libstdc++ against libgcc_s and libnldbl_nonshared
mkdir libgcc
ln -sf /%{_lib}/libgcc_s.so.1 libgcc/libgcc_s.so
sed -ie 's@(SHDEPS)@(SHDEPS) -L'`pwd`'/libgcc -lgcc_s -lnldbl_nonshared@' libstdc++/Makefile.in

rm -rf obj-$RPM_ARCH-linux
mkdir obj-$RPM_ARCH-linux
cd obj-$RPM_ARCH-linux
mkdir ld_hack
cat > ld_hack/ld <<\EOF
#!/bin/sh
case " $* " in *\ -r\ *) exec /usr/bin/ld "$@";; esac
exec /usr/bin/ld --build-id -z noexecstack "$@"
EOF
chmod 755 ld_hack/ld
export PATH=`pwd`/ld_hack/${PATH:+:$PATH}:/sbin:/usr/sbin
../configure  --prefix=/usr \
	--enable-shared --enable-threads \
	--enable-languages=c,c++ \
	--enable-cpp \
	$RPM_ARCH-redhat-linux

touch ../gcc/c-gperf.h
make MAKEINFO="makeinfo --no-split"  bootstrap-lean

%install
rm -rf $RPM_BUILD_ROOT
cd obj-$RPM_ARCH-linux
export PATH=`pwd`/ld_hack/${PATH:+:$PATH}:/sbin:/usr/sbin
make install \
	prefix=$RPM_BUILD_ROOT%{_prefix} \
	mandir=$RPM_BUILD_ROOT%{_mandir} \
	infodir=$RPM_BUILD_ROOT%{_infodir} \
	MAKEINFO="makeinfo --no-split"
mv -f $RPM_BUILD_ROOT%{_bindir}/gcc{,295}
mv -f $RPM_BUILD_ROOT%{_bindir}/g++{,295}
rm -f $RPM_BUILD_ROOT%{_bindir}/*[^5]
rm -rf $RPM_BUILD_ROOT%{_infodir} $RPM_BUILD_ROOT%{_mandir}
rm -rf $RPM_BUILD_ROOT%{_prefix}/s390*
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/gcc-lib/*/*/libstdc++.a
mv $RPM_BUILD_ROOT%{_prefix}/lib/libstdc++*.a \
  $RPM_BUILD_ROOT%{_prefix}/lib/libstdc++.a
mv $RPM_BUILD_ROOT%{_prefix}/lib/libstdc++.a \
  $RPM_BUILD_ROOT%{_prefix}/lib/gcc-lib/*/*/
%ifarch s390x
ln -sf ../../../../lib64/libstdc++-libc6.2-2.so.3 \
  $RPM_BUILD_ROOT%{_prefix}/lib/gcc-lib/*/*/libstdc++.so
%else
ln -sf ../../../libstdc++-libc6.2-2.so.3 \
  $RPM_BUILD_ROOT%{_prefix}/lib/gcc-lib/*/*/libstdc++.so
%endif
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/*.a{,.3} 
%ifarch s390x
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib64
mv -f $RPM_BUILD_ROOT%{_prefix}/lib/lib*so* $RPM_BUILD_ROOT%{_prefix}/lib64/
%endif
echo '' | gcc $RPM_OPT_FLAGS -nostdlib -shared -fpic -xc - \
  -o $RPM_BUILD_ROOT%{_prefix}/%{_lib}/libstdc++-3-libc6.1-2-2.10.0.so \
  -Wl,-soname,libstdc++-libc6.1-2.so.3 -L$RPM_BUILD_ROOT%{_prefix}/%{_lib} \
  -lstdc++-3-libc6.2-2-2.10.0
chmod 755 $RPM_BUILD_ROOT%{_prefix}/%{_lib}/lib*.so
strip -g -R .comment $RPM_BUILD_ROOT%{_prefix}/%{_lib}/lib*.so
/sbin/ldconfig -n $RPM_BUILD_ROOT%{_prefix}/%{_lib}

ar rs libgcc_eh.a
install -m 644 libgcc_eh.a $RPM_BUILD_ROOT%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/

rm -rf $RPM_BUILD_ROOT%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/[Ssi]*
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/c[^r]*
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/libstdc++*
rm -f $RPM_BUILD_ROOT%{_bindir}/gcc295
rm -f $RPM_BUILD_ROOT%{_bindir}/g++295
rm -rf $RPM_BUILD_ROOT%{_includedir}/g++-3

%clean
rm -rf $RPM_BUILD_ROOT

%post -n compat-libstdc++-295 -p /sbin/ldconfig

%postun -n compat-libstdc++-295 -p /sbin/ldconfig

%files -n compat-libstdc++-295
%defattr(-,root,root)
%doc README* COPYING COPYING.LIB
%{_prefix}/%{_lib}/libstdc++*libc6.*.so*

%files -n compat-libgcc-295
%defattr(-,root,root)
%dir %{_prefix}/lib/gcc-lib
%dir %{_prefix}/lib/gcc-lib/%{_target_platform}
%dir %{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3
%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/libgcc.a
%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/libgcc_eh.a
%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/crtbegin.o
%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/crtbeginS.o
%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/crtend.o
%{_prefix}/lib/gcc-lib/%{_target_platform}/2.95.3/crtendS.o

%changelog
* Tue May 18 2010 Jakub Jelinek  <jakub@redhat.com> 2.95.3-86.el6
- ensure libstdc++.so is linked with -Wl,-z,noexecstack (#592849)

* Wed Dec 16 2009 Jakub Jelinek <jakub@redhat.com> 2.95.3-85.el6
- rebuilt for RHEL 6

* Tue Aug 22 2006 Jakub Jelinek <jakub@redhat.com> 2.95.3-85
- link libstdc++.so against libgcc_s and libnldbl_nonshared

* Fri Aug 18 2006 Jakub Jelinek <jakub@redhat.com> 2.95.3-84
- make sure __dso_handle is hidden

* Thu Aug 10 2006 Jakub Jelinek <jakub@redhat.com> 2.95.3-83
- rebuilt for RHEL5

* Fri Oct 15 2004 Jakub Jelinek <jakub@redhat.com> 2.95.3-81
- removed compat-gcc-legacy, renamed compat-libstdc++ to
  compat-libstdc++-295 and added compat-libgcc-295 package

* Fri Aug 13 2004 Jakub Jelinek <jakub@redhat.com> 7.2-2.95.3.80
- rename to compat-gcc-legacy, only include the compiler on s390,
  not s390x

* Tue Jul 13 2004 Jakub Jelinek <jakub@redhat.com> 7.2-2.95.3.79
- add compat-gcc-unsupported subpackage

* Thu Nov  6 2003 Jakub Jelinek <jakub@redhat.com> 7.2-2.95.3.78
- force __udiv_w_sdiv from libgcc.a into libstdc++.so on s390
  (#109061)

* Wed Sep 17 2003 Jakub Jelinek <jakub@redhat.com> 7.2-2.95.3.77
- changed BuildRoot so that it doesn't clash with normal gcc
- remove %%{_smp_mflags}, makefiles apparently aren't ready for -jN

* Tue Sep 16 2003 Phil Knirsch <pknirsch@redhat.com> 7.2-2.95.3.76
- Added gcc-2.95.3-s390-4 and gcc-2.95.3-s390-5 patches from IBM.

* Wed Sep 10 2003 Jakub Jelinek <jakub@redhat.com> 7.2-2.95.3.75
- include libstdc++-3-libc6.1-2.so.3 stub library

* Mon Sep  8 2003 Jakub Jelinek <jakub@redhat.com> 7.2-2.95.3.74
- use int ssize_t on s390 and long int off64_t on s390x so that
  name mangling is identical
- strip the library

* Mon Sep  8 2003 Jakub Jelinek <jakub@redhat.com> 7.2-2.95.3.73
- changed into compatibility package
- link libstdc++ against libgcc_s.so.1

* Tue Mar 19 2002 Phil Knirsch <pknirsch@redhat.com>
- Added latest official IBM gcc patch (gcc-2.95.3-s390-3).

* Fri Feb 08 2002 Phil Knirsch <pknirsch@redhat.com>
- Reenabled glibc224 patch as we are using glibc 2.2.4 now for 7.1

* Thu Jan 31 2002 David Sainty <dsainty@redhat.com> 2.95.3-0.71.2sx
- add in gcc-2.95.2-bogushack-s390x patch to fix cpp compiles

* Thu Jan 31 2002 David Sainty <dsainty@redhat.com>
- disable glibc224 patch - we don't have glibc-2.2.4 on 7.1

* Wed Oct 24 2001 Karsten Hopp <karsten@redhat.de>
- add -undef patch to ignore unsupported flag

* Tue Oct 16 2001 David Sainty <dsainty@redhat.com>
- use 2.95.3 with following patches:
	- s390 and s390-1 and s390-2 (v.recent) IBM patches
	- glibc224 and libio patches

* Sat Dec 09 2000 Florian La Roche <Florian.LaRoche@redhat.de>
- use 2.95.2 with the following patches:
	- current head of cvs
	- S390 patch from IBM: gcc-2.95.2.4
	- spec file is based on the standard Red Hat Linux 7 one plus
	  a version ported from Red Hat Linux 6.2 to S390 by
		- Oliver Paukstadt <opaukstadt@millenux.com>
		- Fritz Elfert <felfert@to.com>
