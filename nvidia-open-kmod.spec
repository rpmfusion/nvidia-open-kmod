#
# SPDX-FileCopyrightText: 2022 Nicolas Chauvet <kwizart@gmail.com>
# SPDX-License-Identifier: AGPL-3.0
#

%if 0%{?fedora}
%global buildforkernels akmod
%endif
%global debug_package %{nil}
%global _kmodtool_zipmodules 0

Name:          nvidia-open-kmod
Epoch:         3
Version:       570.169
# Taken over by kmodtool
Release:       1%{?dist}
Summary:       NVIDIA open display driver kernel module
License:       GPLv2 and MIT
URL:           https://github.com/NVIDIA/open-gpu-kernel-modules

Source0:       %{url}/archive/%{version}/open-gpu-kernel-modules-%{version}.tar.gz
Source11:      nvidia-open-kmodtool-excludekernel-filterfile
Patch0:        make_modeset_default.patch
Patch1:        linker_fix.patch

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
%if 0%{?_with_nvidia_defaults:1}
echo "Using original nvidia defaults"
%else
echo "Set nvidia to fbdev=1 modeset=1"
%patch -P0 -p1 -d open-gpu-kernel-modules-%{version}
%endif
%patch -P1 -p1 -d open-gpu-kernel-modules-%{version}

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
    %make_build \
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
* Tue Jun 24 2025 Nicolas Chauvet <kwizart@gmail.com> - 3:570.169-1
- Update to 570.169

* Mon May 19 2025 Leigh Scott <leigh123linux@gmail.com> - 3:570.153.02-1
- Update to 570.153.02 release

* Tue Apr 22 2025 Leigh Scott <leigh123linux@gmail.com> - 3:570.144-1
- Update to 570.144 release

* Fri Apr 11 2025 Leigh Scott <leigh123linux@gmail.com> - 3:570.133.07-2
- Force build to use std=gnu17

* Tue Mar 18 2025 Leigh Scott <leigh123linux@gmail.com> - 3:570.133.07-1
- Update to 570.133.07 release

* Thu Mar 06 2025 Leigh Scott <leigh123linux@gmail.com> - 3:570.124.04-2
- Disable module compression everywhere

* Thu Feb 27 2025 Leigh Scott <leigh123linux@gmail.com> - 3:570.124.04-1
- Update to 570.124.04 release

* Thu Jan 30 2025 Leigh Scott <leigh123linux@gmail.com> - 3:570.86.16-1
- Update to 570.86.16 beta

* Wed Jan 29 2025 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3:565.77-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Fri Dec 13 2024 Leigh Scott <leigh123linux@gmail.com> - 3:565.77-2
- Fix linker patch

* Thu Dec 05 2024 Leigh Scott <leigh123linux@gmail.com> - 3:565.77-1
- Update to 565.77 release

* Wed Oct 30 2024 Leigh Scott <leigh123linux@gmail.com> - 3:565.57.01-2
- Fix linker issue

* Tue Oct 22 2024 Leigh Scott <leigh123linux@gmail.com> - 3:565.57.01-1
- Update to 565.57.01 beta

* Wed Aug 21 2024 Leigh Scott <leigh123linux@gmail.com> - 3:560.35.03-1
- Update to 560.35.03 Release

* Mon Aug 19 2024 Leigh Scott <leigh123linux@gmail.com> - 3:560.31.02-2
- Enable nvidia fbdev
- Fix nvidia framebuffer with 6.11rc

* Tue Aug 06 2024 Leigh Scott <leigh123linux@gmail.com> - 3:560.31.02-1
- Update to 560.31.02 beta

* Sat Aug 03 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3:560.28.03-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Tue Jul 23 2024 Leigh Scott <leigh123linux@gmail.com> - 3:560.28.03-1
- Update to 560.28.03 beta

* Mon Jul 01 2024 Leigh Scott <leigh123linux@gmail.com> - 3:555.58.02-1
- Update to 555.58.02

* Thu Jun 27 2024 Leigh Scott <leigh123linux@gmail.com> - 3:555.58-1
- Update to 555.58 release

* Thu Jun 06 2024 Leigh Scott <leigh123linux@gmail.com> - 3:555.52.04-1
- Update to 555.52.04 beta

* Sat Jun 01 2024 Leigh Scott <leigh123linux@gmail.com> - 3:555.42.02-2
- Patch for kernel-6.10rc

* Tue May 21 2024 Leigh Scott <leigh123linux@gmail.com> - 3:555.42.02-1
- Update to 555.42.02 beta

* Sat May 11 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.78-3
- Adjust patch to disable nvidia fbdev

* Sat May 11 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.78-2
- Default enable nvidia modeset and fbdev

* Fri Apr 26 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.78-1
- Update to 550.78 release

* Wed Apr 17 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.76-1
- Update to 550.76 release

* Wed Mar 20 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.67-1
- Update to 550.67 release

* Fri Mar 01 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.54.14-2
- Fix gcc14 compile issue (rfbz#6882)

* Sat Feb 24 2024 Leigh Scott <leigh123linux@gmail.com> - 3:550.54.14-1
- Update to 550.54.14 release

* Sun Feb 04 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 3:550.40.07-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

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

