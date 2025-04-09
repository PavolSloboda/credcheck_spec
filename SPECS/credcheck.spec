Name: credcheck
Version: 3.0
Release: %autorelease 
Summary: PostreSQL extension for credential checking
License: PostgreSQL
URL: https://github.com/HexaCluster/credcheck
Source0: https://github.com/HexaCluster/%{name}/archive/refs/tags/v%{version}.tar.gz
Source1: %{name}.te
Patch0: enable_cracklib.patch
Patch1: upstream_db7c811a02f286b9ba3e81a219826bf47eca6d4e.patch

%global deny_easy_pass 1

BuildRequires: make postgresql-server-devel gcc
%if %{deny_easy_pass} == 1
BuildRequires: cracklib-devel cracklib-dicts selinux-policy-devel
%endif

#the lowest version of postgresql on fedora 42 is 16.0
#therefore the requirement of this  package for version 10.0 and up 
#(12.0 when the Password Reuse Policy feature is used) is automatically
#satisfied and there is no need to specify the lowest version of
#postgresql-server in the Requires macro
Requires: postgresql-server-any
%if %{deny_easy_pass} == 1
Requires: cracklib-dicts
Requires(post): libselinux-utils
%endif

%description
The credcheck PostgreSQL extension provides few general credential checks,
which will be evaluated during the user creation, during the password change
and user renaming. By using this extension, we can define a set of rules:

    allow a specific set of credentials
    reject a certain type of credentials
    deny password that can be easily cracked
    enforce use of an expiration date with a minimum of day for a password
    define a password reuse policy
    define the number of authentication failure allowed before a user is banned

This extension provides all the checks as configurable parameters.
The default configuration settings, will not enforce any complex checks
and will try to allow most of the credentials.
By using SET credcheck.<check-name> TO <some value>; command, enforce new
settings for the credential checks. The settings can only be changed 
by a superuser.

%prep
%setup -q
%if %{deny_easy_pass} == 1
#uncomments the lines in the makefile necessary for
#using the version that forbids easily crackable passwords
%patch 0 -p1
%endif
%patch 1 -p1

#TODO
#save a database as a test

%build
%make_build

%install
%make_install
#creates the credcheck file to contain the patches
mkdir -p %{buildroot}%{_datadir}/%{name}
mv %{buildroot}%{_datadir}/pgsql/extension/%{name}--*--*.sql %{buildroot}%{_datadir}/%{name}
%if %{deny_easy_pass} == 1
mkdir -p %{buildroot}%{_datadir}/selinux/packages/targeted
cp %{SOURCE1} %{buildroot}%{_datadir}
cd %{buildroot}%{_datadir} && make -f /usr/share/selinux/devel/Makefile %{name}.pp
mv %{buildroot}%{_datadir}/%{name}.pp %{buildroot}%{_datadir}/selinux/packages/targeted
rm %{buildroot}%{_datadir}/%{name}.{te,fc,if}
rm -rf %{buildroot}%{_datadir}/tmp
%endif

#TODO
#this needs to be done but the question is whether by the package install or the user
#it also requires the words package to function
#%if %{deny_easy_pass} == 1
##this is necessary or the password is easily cracked check
##goes off on everything (the files can't even be created as empty)
#mkdict /usr/share/dict/* | sudo cracklib-packer /usr/lib/cracklib_dict
#also needs to append credcheck to shared_preloaded_libraries in /var/lib/pgsql/data/postgresql.conf
#and then restart the postgresql.service
#%endif

%post
%if %{deny_easy_pass} == 1
%selinux_modules_install -s "targeted" %{_datadir}/selinux/packages/targeted/%{name}.pp
%endif

%postun
%if %{deny_easy_pass} == 1
%selinux_modules_uninstall -s "targeted" %{name}
%endif

%files
%doc README.md 
%license LICENSE
%{_libdir}/pgsql/%{name}.so
%{_datadir}/pgsql/extension/%{name}--%{version}.0.sql
%{_datadir}/pgsql/extension/%{name}.control
%{_datadir}/%{name}/%{name}--*--*.sql
%if %{deny_easy_pass} == 1
%{_datadir}/selinux/packages/targeted/%{name}.pp
%endif

%changelog
%autochangelog
