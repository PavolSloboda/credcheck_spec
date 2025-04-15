#controls whether or not cracklib will be used during the build of the package
#building without cracklib will result in the package not having the
#deny_easy_pass functionality (checking for easily crackable passwords
#using cracklib and dictionaries)
%bcond_without cracklib
Name: credcheck
Version: 3.0
Release: %autorelease 
Summary: PostgreSQL extension for credential checking
License: PostgreSQL
URL: https://github.com/HexaCluster/%{name}
Source0: https://github.com/HexaCluster/%{name}/archive/refs/tags/v%{version}.tar.gz
%if %{with cracklib}
#a SELinux rule template to enable reading of the dictionaries
#provided by the cracklib-dict package
#an augmented version of the rule used by cracklib-password-check-plugin
#for mariadb: https://mariadb.com/kb/en/cracklib-password-check-plugin/
Source1: %{name}.te
#patch containing the changes to the Makefile necessary to compile the package
#to use the cracklib package as mentioned in README.md on lines 42 and 43
#https://github.com/HexaCluster/credcheck/blob/master/README.md
Patch0: enable_cracklib.patch
%endif
#patch containing the latest license change taken from commit:
#https://github.com/HexaCluster/credcheck/commit/db7c811a02f286b9ba3e81a219826bf47eca6d4e
Patch1: upstream_db7c811a02f286b9ba3e81a219826bf47eca6d4e.patch

BuildRequires: make postgresql-server-devel gcc
%if %{with cracklib}
BuildRequires: cracklib-devel cracklib-dicts selinux-policy-devel
%endif

#the lowest version of postgresql on fedora 42 is 16.0
#therefore the requirement of this  package for version 10.0 and up 
#(12.0 when the Password Reuse Policy feature is used) is automatically
#satisfied and there is no need to specify the lowest version of
#postgresql-server in the Requires macro
Requires: postgresql-server-any
%if %{with cracklib}
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
%autosetup

%build
%make_build

%install
%make_install
#creates the credcheck file to contain the patches
mkdir -p %{buildroot}%{_datadir}/%{name}
mv %{buildroot}%{_datadir}/pgsql/extension/%{name}--*--*.sql %{buildroot}%{_datadir}/%{name}
%if %{with cracklib}
mkdir -p %{buildroot}%{_datadir}/%{name}/selinux
cp -p %{SOURCE1} %{buildroot}%{_datadir}
cd %{buildroot}%{_datadir} && make -f /usr/share/selinux/devel/Makefile %{name}.pp
mv %{buildroot}%{_datadir}/%{name}.pp %{buildroot}%{_datadir}/%{name}/selinux
rm %{buildroot}%{_datadir}/%{name}.{te,fc,if}
rm -rf %{buildroot}%{_datadir}/tmp
%endif

%if %{with cracklib}
%post
%selinux_modules_install -s "targeted" %{_datadir}/%{name}/selinux/%{name}.pp

%postun
%selinux_modules_uninstall -s "targeted" %{name}
%endif

%files
%doc README.md 
%license LICENSE
%{_libdir}/pgsql/%{name}.so
%{_datadir}/pgsql/extension/%{name}--%{version}.0.sql
%{_datadir}/pgsql/extension/%{name}.control
%{_datadir}/%{name}/%{name}--*--*.sql
%dir %{_datadir}/%{name}
%if %{with cracklib}
%{_datadir}/%{name}/selinux/%{name}.pp
%dir %{_datadir}/%{name}/selinux
%endif

%changelog
%autochangelog
