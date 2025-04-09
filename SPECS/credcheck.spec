Name: credcheck
Version: 3.0
Release: %autorelease 
Summary: PostreSQL extension for credential checking
#TODO
#the license does not match
#it does match the MIT - 0 License but not in name
License: PostgreSQL License
URL: https://github.com/HexaCluster/credcheck
Source: https://github.com/HexaCluster/credcheck/archive/refs/tags/v3.0.tar.gz

%global deny_easy_pass 1

BuildRequires: make postgresql-server-devel gcc
%if %{deny_easy_pass} == 1
BuildRequires: cracklib-devel cracklib-dicts selinux-policy-devel
%endif
#the lowest version on fedora 42 is 16.0
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
settings for the credential checks. The settings can only be changed by a superuser.

%prep
%setup

#TODO
#save a database as a test

%build
%if %{deny_easy_pass} == 1
#uncomments the lines in the makefile necessary for
#using the version that forbids easily crackable passwords
sed -i 's/#PG_CPPFLAGS/PG_CPPFLAGS/g' %{_builddir}/%{name}-%{version}/Makefile
sed -i 's/#SHLIB_LINK/SHLIB_LINK/g' %{_builddir}/%{name}-%{version}/Makefile
sed -i 's|-DCRACKLIB_DICTPATH=\"/usr/lib/cracklib_dict\"|-DCRACKLIB_DICTPATH=\"/usr/share/cracklib/pw_dict\"|g' %{_builddir}/%{name}-%{version}/Makefile
%endif
%make_build

%install
%make_install
#creates the credcheck file to contain the patches
mkdir -p %{buildroot}%{_datadir}/credcheck
mv %{buildroot}%{_datadir}/pgsql/extension/credcheck--*--*.sql %{buildroot}%{_datadir}/credcheck
mkdir -p %{buildroot}%{_datadir}/selinux/packages/targeted
cp %{_sourcedir}/credcheck.te %{buildroot}%{_datadir}
cd %{buildroot}%{_datadir} && make -f /usr/share/selinux/devel/Makefile credcheck.pp
mv %{buildroot}%{_datadir}/credcheck.pp %{buildroot}%{_datadir}/selinux/packages/targeted
rm %{buildroot}%{_datadir}/credcheck.te
rm %{buildroot}%{_datadir}/credcheck.fc
rm %{buildroot}%{_datadir}/credcheck.if
rm -rf %{buildroot}%{_datadir}/tmp

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
sudo semodule -i -s "targeted" %{_datadir}/selinux/packages/targeted/credcheck.pp

%postun
sudo semodule -r -s "targeted" credcheck

%files
%{_libdir}/pgsql/credcheck.so
%{_datadir}/pgsql/extension/credcheck--%{version}.0.sql
%{_datadir}/credcheck/credcheck--*--*.sql
%{_datadir}/pgsql/extension/credcheck.control
%doc README.md 
%license LICENSE

%changelog
%autochangelog
