#Module-Specific definitions
%define mod_name mod_log_dbd
%define mod_conf A26_%{mod_name}.conf
%define mod_so %{mod_name}.so

%define apache_version 2.2.4

Summary:	Writes access logs to a database using the APR DBD framework
Name:		apache-%{mod_name}
Version:	0.2
Release:	%mkrel 11
Group:		System/Servers
License:	BSD
URL:		http://bfoz.net/projects/mod_log_dbd/
Source0: 	http://bfoz.net/projects/mod_log_dbd/release/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= %{apache_version}
Requires(pre):	apache >= %{apache_version}
Requires:	apache-conf >= %{apache_version}
Requires:	apache >= %{apache_version}
BuildRequires:	apache-devel >= %{apache_version}
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_log_dbd is a module for Apache 2.2+ that writes access logs to a database
using the APR DBD framework. It's designed for simplicity and speed, and
therefore lacks some of the features of other logging modules. It does however
automatically create any needed tables and columns.

%prep

%setup -q -n %{mod_name}-%{version}

cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# silly bugs
perl -pi -e "s|include/apache22|include/apache|g" configure*
perl -pi -e "s|apxs|%{_sbindir}/apxs|g" Makefile*
perl -pi -e "s|-module|-module -avoid-version|g" Makefile*

%build
rm -f fonfigure
autoreconf -fi

%configure2_5x --localstatedir=/var/lib \
    --with-apache=%{_prefix}

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/%{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
