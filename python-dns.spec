%if 0%{?fedora} > 12
%global with_python3 1
%else
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%endif

Name:           python-dns
Version:        1.10.0
Release:        5%{?dist}
Summary:        DNS toolkit for Python

Group:          Development/Languages
License:        MIT
URL:            http://www.dnspython.org/
Source0:        http://www.dnspython.org/kits/%{version}/dnspython-%{version}.tar.gz
Source1:        http://www.dnspython.org/kits/%{version}/dnspython-%{version}.tar.gz.asc
Source2:        http://www.dnspython.org/kits3/%{version}/dnspython3-%{version}.tar.gz
Source3:        http://www.dnspython.org/kits3/%{version}/dnspython3-%{version}.tar.gz.asc
Patch1:         dnspython-1.10.1-tlsa.patch
# Patch2 https://github.com/rthalley/dnspython/issues/47
Patch2:         0002-dns-loc-records-parsing.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
BuildRequires: python-setuptools
%endif

%if 0%{?with_python3}
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%endif

%description
dnspython is a DNS toolkit for Python. It supports almost all record
types. It can be used for queries, zone transfers, and dynamic
updates. It supports TSIG authenticated messages and EDNS0.

dnspython provides both high and low level access to DNS. The high
level classes perform queries for data of a given name, type, and
class, and return an answer set. The low level classes allow direct
manipulation of DNS zones, messages, names, and records.


%if 0%{?with_python3}
%package     -n python3-dns
Summary:        DNS toolkit for Python 3
Group:          Development/Languages

%description -n python3-dns
dnspython3 is a DNS toolkit for Python 3. It supports almost all record
types. It can be used for queries, zone transfers, and dynamic
updates. It supports TSIG authenticated messages and EDNS0.

dnspython3 provides both high and low level access to DNS. The high
level classes perform queries for data of a given name, type, and
class, and return an answer set. The low level classes allow direct
manipulation of DNS zones, messages, names, and records.
%endif


%prep
%setup -q -n dnspython-%{version}
%setup -T -D -a 2 -q -n dnspython-%{version}
%patch1 -p1 -b .tlsa
%patch2 -p1

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a dnspython3-%{version} %{py3dir}
%endif

# strip executable permissions so that we don't pick up dependencies
# from documentation
find examples -type f | xargs chmod a-x


%build
CFLAGS="%{optflags}" %{__python} -c 'import setuptools; execfile("setup.py")' build

%if 0%{?with_python3}
pushd %{py3dir}
CFLAGS="%{optflags}" %{__python3} setup.py build
popd
%endif


%install
rm -rf %{buildroot}
%{__python} -c 'import setuptools; execfile("setup.py")' install --skip-build --root %{buildroot}

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} -c 'import setuptools; exec(open("setup.py").read())' install \
    --skip-build --root %{buildroot}
popd
%endif


%check
pushd tests
# skip one test because it queries the network
for py in *.py
do
        if [ $py != resolver.py ]
        then
                PYTHONPATH=%{buildroot}%{python_sitelib} %{__python} $py
        fi
done

%if 0%{?with_python3}
pushd %{py3dir}/tests
for py in *.py
do
    if [ $py != resolver.py ]
    then
        PYTHONPATH=%{buildroot}%{python3_sitelib} %{__python3} $py
    fi
done
popd
%endif


%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc ChangeLog LICENSE README examples

%{python_sitelib}/*egg-info
%{python_sitelib}/dns

%if 0%{?with_python3}
%files -n python3-dns
%defattr(-,root,root,-)
%doc dnspython3-%{version}/{ChangeLog,LICENSE,README,examples}

%{python3_sitelib}/*egg-info
%{python3_sitelib}/dns
%endif


%changelog
* Tue Jan 28 2014 Robert Kuska <rkuska@redhat.com> - 1.10.0-5
- Patch to fix LOC records parsing
Resolves: rhbz#1056747

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.10.0-4
- Mass rebuild 2013-12-27

* Sat Feb 16 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1.10.0-3
- add python3-dns subpackage (rhbz#911933)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Sep 17 2012 Paul Wouters <pwouters@redhat.com> - 1.10.0-1
- Updated to 1.10.0
- Patch to support TLSA RRtype

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Mar 28 2011 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.9.4-1
-
- dnspython 1.9.4 has been released and is available at
- http://www.dnspython.org/kits/1.9.4/
-
- There is no new functionality in this release; just a few bug fixes
- in RRSIG and SIG code.
-
- I will be eliminating legacy code for earlier versions of DNSSEC in a
- future release of dnspython.

* Fri Mar 25 2011 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.9.3-1
-
- New since 1.9.2:
-
-     A boolean parameter, 'raise_on_no_answer', has been added to
- the query() methods.  In no-error, no-data situations, this
- parameter determines whether NoAnswer should be raised or not.
- If True, NoAnswer is raised.  If False, then an Answer()
- object with a None rrset will be returned.
-
- Resolver Answer() objects now have a canonical_name field.
-
- Rdata now have a __hash__ method.
-
- Bugs fixed since 1.9.2:
-
-        Dnspython was erroneously doing case-insensitive comparisons
- of the names in NSEC and RRSIG RRs.
-
- We now use "is" and not "==" when testing what section an RR
- is in.
-
- The resolver now disallows metaqueries.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Nov 23 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.9.2-1
- It's brown paper bag time :) The fix for the import problems was
- actually bad, but didn't show up in testing because the test suite's
- conditional importing code hid the problem.
-
- Any, 1.9.2 is out.
-
- Sorry for the churn!

* Mon Nov 22 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.9.1-1
- New since 1.9.0:
-
-        Nothing.
-
- Bugs fixed since 1.9.0
-
-        The dns.dnssec module didn't work with DSA due to namespace
-        contamination from a "from"-style import.
-
- New since 1.8.0:
-
-        dnspython now uses poll() instead of select() when available.
-
-        Basic DNSSEC validation can be done using dns.dnsec.validate()
-        and dns.dnssec.validate_rrsig() if you have PyCrypto 2.3 or
-        later installed.  Complete secure resolution is not yet
-        available.
-
-        Added key_id() to the DNSSEC module, which computes the DNSSEC
-        key id of a DNSKEY rdata.
-
-        Added make_ds() to the DNSSEC module, which returns the DS RR
-        for a given DNSKEY rdata.
-
-        dnspython now raises an exception if HMAC-SHA284 or
-        HMAC-SHA512 are used with a Python older than 2.5.2.  (Older
-        Pythons do not compute the correct value.)
-
-        Symbolic constants are now available for TSIG algorithm names.
-
- Bugs fixed since 1.8.0
-
-        dns.resolver.zone_for_name() didn't handle a query response
-        with a CNAME or DNAME correctly in some cases.
-
-        When specifying rdata types and classes as text, Unicode
-        strings may now be used.
-
-        Hashlib compatibility issues have been fixed.
-
-        dns.message now imports dns.edns.
-
-        The TSIG algorithm value was passed incorrectly to use_tsig()
-        in some cases.

* Fri Aug 13 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.8.0-3
- Add a patch from upstream to fix a Python 2.7 issue.

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 1.8.0-2.1
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Wed Jan 27 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.8.0-1.1
- Fix error

* Wed Jan 27 2010 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.8.0-1
- New since 1.7.1:
-
-  Support for hmac-sha1, hmac-sha224, hmac-sha256, hmac-sha384 and
-  hmac-sha512 has been contributed by Kevin Chen.
-
-  The tokenizer's tokens are now Token objects instead of (type,
-  value) tuples.
-
- Bugs fixed since 1.7.1:
-
-  Escapes in masterfiles now work correctly.  Previously they were
-  only working correctly when the text involved was part of a domain
-  name.
-
-  When constructing a DDNS update, if the present() method was used
-  with a single rdata, a zero TTL was not added.
-
-  The entropy pool needed locking to be thread safe.
-
-  The entropy pool's reading of /dev/random could cause dnspython to
-  block.
-
-  The entropy pool did buffered reads, potentially consuming more
-  randomness than we needed.
-
-  The entropy pool did not seed with high quality randomness on
-  Windows.
-
-  SRV records were compared incorrectly.
-
-  In the e164 query function, the resolver parameter was not used.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jun 19 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.7.1-1
- New since 1.7.0:
-
-        Nothing
-
- Bugs fixed since 1.7.0:
-
-        The 1.7.0 kitting process inadventently omitted the code for the
-        DLV RR.
-
-        Negative DDNS prerequisites are now handled correctly.

* Fri Jun 19 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.7.0-1
- New since 1.6.0:
-
-        Rdatas now have a to_digestable() method, which returns the
-        DNSSEC canonical form of the rdata, suitable for use in
-        signature computations.
-
-        The NSEC3, NSEC3PARAM, DLV, and HIP RR types are now supported.
-
-        An entropy module has been added and is used to randomize query ids.
-
-        EDNS0 options are now supported.
-
-        UDP IXFR is now supported.
-
-        The wire format parser now has a 'one_rr_per_rrset' mode, which
-        suppresses the usual coalescing of all RRs of a given type into a
-        single RRset.
-
-        Various helpful DNSSEC-related constants are now defined.
-
-        The resolver's query() method now has an optional 'source' parameter,
-        allowing the source IP address to be specified.
-
- Bugs fixed since 1.6.0:
-
-        On Windows, the resolver set the domain incorrectly.
-
-        DS RR parsing only allowed one Base64 chunk.
-
-        TSIG validation didn't always use absolute names.
-
-        NSEC.to_text() only printed the last window.
-
-        We did not canonicalize IPv6 addresses before comparing them; we
-        would thus treat equivalent but different textual forms, e.g.
-        "1:00::1" and "1::1" as being non-equivalent.
-
-        If the peer set a TSIG error, we didn't raise an exception.
-
-        Some EDNS bugs in the message code have been fixed (see the ChangeLog
-        for details).

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6.0-3
- Rebuild for Python 2.6

* Fri Aug 29 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.6.0-2
- fix license tag

* Sat Dec  4 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.6.0-1
- Update to 1.6.0

* Tue Oct  9 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.5.0-2
- Follow new Python egg packaging specs

* Thu Jan 11 2007 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.5.0-1
- Update to 1.5.0

* Fri Dec  8 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.4.0-3
- Bump release for rebuild with Python 2.5

* Mon Aug 14 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.4.0-2
- No longer ghost *.pyo files, thus further simplifying the files section.

* Sat Aug  5 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.4.0-1
- Update to 1.4.0
- Remove unneeded python-abi requires
- Remove unneeded python_sitearch macro

* Fri May 26 2006 Jeffrey C. Ollie <jeff@ocjtech.us> - 1.3.5-1
- First version for Fedora Extras

