#
# SPDX-FileCopyrightText: 2022 Nicolas Chauvet <kwizart@gmail.com>
# SPDX-License-Identifier: AGPL-3.0
#

%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}

Name:          nvidia-open-kmod
Epoch:         3
Version:       550.40.07
# Taken over by kmodtool
Release:       1%{?dist}
Summary:       NVIDIA open display driver kernel module
License:       GPLv2 and MIT
URL:           https://github.com/NVIDIA/open-gpu-kernel-modules

Source0:       %{url}/archive/%{version}/open-gpu-kernel-modules-%{version}.tar.gz
Source11:      nvidia-open-kmodtool-excludekernel-filterfile

ExclusiveArch:  x86_64 aarch64

# get the needed BuildRequires (in parts depending on what we build for)
%global AkmodsBuildRequires %{_bindir}/kmodtool, gcc-c++, elfutils-libelf-devel
BuildRequires:  %{AkmodsBuildRequires}

%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }
# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} --filterfile %{SOURCE11} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
The nvidia open %{version} display driver kernel module for kernel %{kversion}.

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}
# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo rpmfusion --kmodname %{name} --filterfile %{SOURCE11} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null
%setup -q -c
# patch loop
%if 0%{?_without_nvidia_kmod_patches:1}
# placeholder
%endif

for kernel_version  in %{?kernel_versions} ; do
    cp -a open-gpu-kernel-modules-%{version} _kmod_build_${kernel_version%%___*}
done

%build
%if 0%{?_without_nvidia_uvm:1}
export NV_EXCLUDE_KERNEL_MODULES="${NV_EXCLUDE_KERNEL_MODULES} nvidia_uvm "
%endif
%if 0%{?_without_nvidia_modeset:1}
export NV_EXCLUDE_KERNEL_MODULES="${NV_EXCLUDE_KERNEL_MODULES} nvidia_modeset "
%endif

for kernel_version in %{?kernel_versions}; do
  pushd _kmod_build_${kernel_version%%___*}/
    make V=1 %{?_smp_mflags} CC=gcc \
        KERNEL_UNAME="${kernel_version%%___*}" SYSSRC="${kernel_version##*___}" \
        IGNORE_CC_MISMATCH=1 IGNORE_XEN_PRESENCE=1 IGNORE_PREEMPT_RT_PRESENCE=1 \
        modules
  popd
done


%install
for kernel_version in %{?kernel_versions}; do
    mkdir -p  %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
    install -D -m 0755 _kmod_build_${kernel_version%%___*}/kernel-open/nvidia*.ko \
         %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
done
%{?akmod_install}



%changelog
* Wed Jan 24 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.40.07-1
- Update to 550.40.07 beta

* Wed Nov 22 2023 Leigh Scott <leigh123linux@gmail.com> - 3:545.29.06-1
- Update to 545.29.06 release

* Wed Oct 18 2023 Leigh Scott <leigh123linux@gmail.com> - 3:545.23.06-1
- Update to 545.23.06 beta

* Fri Sep 22 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.113.01-1
- Update to 535.113.01

* Tue Aug 22 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.104.05-1
- Update to 535.104.05

* Wed Aug 09 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.98-1
- Update to 535.98

* Thu Aug 03 2023 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3:535.86.05-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Tue Jul 18 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.86.05-1
- Update to 535.86.05

* Thu Jun 15 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.54.03-1
- Update to 535.54.03

* Tue May 30 2023 Leigh Scott <leigh123linux@gmail.com> - 3:535.43.02-1
- Update to 535.43.02 beta

* Fri Mar 24 2023 Leigh Scott <leigh123linux@gmail.com> - 3:530.41.03-1
- Update to 530.41.03

* Sun Mar 05 2023 Leigh Scott <leigh123linux@gmail.com> - 3:530.30.02-1
- Update to 530.30.02 beta

* Fri Feb 10 2023 Leigh Scott <leigh123linux@gmail.com> - 3:525.89.02-1
- Update to 525.89.02

* Thu Jan 19 2023 Leigh Scott <leigh123linux@gmail.com> - 3:525.85.05-1
- Update to 525.85.05

* Thu Jan 05 2023 Leigh Scott <leigh123linux@gmail.com> - 3:525.78.01-1
- Update to 525.78.01

* Sun Dec 11 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:525.60.11-1
- Update to 525.60.11

* Thu Nov 10 2022 Leigh Scott <leigh123linux@gmail.com> - 3:525.53-1
- Update to 525.53 beta

* Wed Nov 09 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:520.56.06-2
- Add gcc-g++ - rfbz#6473

* Tue Nov 08 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:520.56.06-1
- Update to 520.56.06

* Wed Sep 21 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.76-1
- Update to 515.76

* Mon Aug 08 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.65.01-1
- Update to 515.65.01

* Mon Aug 08 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3:515.57-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild and ffmpeg
  5.1

* Mon Jul 04 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:515.57-1
- Update to 515.57

* Wed Jun 01 2022 Nicolas Chauvet <kwizart@gmail.com> - 3:515.48.07-3
- Switch to kernel-open

* Wed May 11 2022 Leigh Scott <leigh123linux@gmail.com> - 3:515.43.04-1
- Update to 515.43.04 beta

