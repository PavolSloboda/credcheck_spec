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
BuildRequires: cracklib-devel
%endif
Requires: postgresql >= 12.0
%if %{deny_easy_pass} == 1
Requires: cracklib cracklib-dicts words
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
%endif
%make_build

%install
%make_install
%if %{deny_easy_pass} == 1
#this is necessary or the password is easily cracked check
#goes off on everything (the files can't even be created as empty)
mkdict /usr/share/dict/* | sudo cracklib-packer /usr/lib/cracklib_dict
%endif

#creates the credcheck file to contain the patches
mkdir -p %{buildroot}%{_datadir}/credcheck
cp updates/* %{buildroot}%{_datadir}/credcheck

%files
%{_libdir}/pgsql/credcheck.so
%{_datadir}/pgsql/extension/credcheck--%{version}.0.sql
%{_datadir}/credcheck/credcheck--*--*.sql
%{_datadir}/pgsql/extension/credcheck.control
%exclude %{_datadir}/pgsql/extension/credcheck--*--*.sql
%doc README.md 
%license LICENSE

%changelog
%autochangelog
