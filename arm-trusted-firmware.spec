# Binaries not used in standard manner so debuginfo is useless
%global debug_package %{nil}

Name:		arm-trusted-firmware
Version:	2.10.0
Release:	1
Summary:	ARM Trusted Firmware
License:	BSD
Group:		Development/C
URL:		https://github.com/ARM-software/arm-trusted-firmware/wiki
Source0:	https://github.com/ARM-software/arm-trusted-firmware/archive/v%{version}.tar.gz
Source1:	https://src.fedoraproject.org/rpms/arm-trusted-firmware/raw/rawhide/f/aarch64-bl31

BuildRequires:	dtc
BuildRequires:	gcc

%ifnarch %{arm}
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-gcc-bootstrap
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-binutils
%endif
%ifnarch %{armx}
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-binutils
%endif

%description
ARM Trusted firmware is a reference implementation of secure world software for
ARMv8-A including Exception Level 3 (EL3) software. It provides a number of
standard ARM interfaces like Power State Coordination (PSCI), Trusted Board
Boot Requirements (TBBR) and Secure Monitor.

Note: the contents of this package are generally just consumed by bootloaders
such as u-boot. As such the binaries aren't of general interest to users.

%package -n arm-trusted-firmware-armv8
Summary:	ARM Trusted Firmware for ARMv8-A
Group:		Development/C

%description -n arm-trusted-firmware-armv8
ARM Trusted Firmware binaries for various  ARMv8-A SoCs.

Note: the contents of this package are generally just consumed by bootloaders
such as u-boot. As such the binaries aren't of general interest to users.

%prep
%autosetup -p1 -n %{name}-%{version}

cp %{SOURCE1} .

# Fix the name of the cross compile for the rk3399 Cortex-M0 PMU
sed -i 's/arm-none-eabi-/armv7hnl-linux-gnueabihf-/' plat/rockchip/rk3399/drivers/m0/Makefile

%build
%undefine _auto_set_build_flags

for soc in $(cat aarch64-bl31)
do
# At the moment we're only making the secure firmware (bl31)
make HOSTCC="gcc $RPM_OPT_FLAGS" CROSS_COMPILE="aarch64-openmandriva-linux-gnu-" PLAT=$(echo $soc) bl31
done

%install
mkdir -p %{buildroot}%{_datadir}/%{name}

# At the moment we just support adding bl31.bin
for soc in $(cat %{_arch}-bl31)
do
mkdir -p %{buildroot}%{_datadir}/%{name}/$(echo $soc)/
 for file in bl31.bin
 do
  if [ -f build/$(echo $soc)/release/$(echo $file) ]; then
    install -p -m 0644 build/$(echo $soc)/release/$(echo $file) /%{buildroot}%{_datadir}/%{name}/$(echo $soc)/
  fi
 done
done

# Rockchips wants the bl31.elf, plus rk3399 wants power management co-processor bits
for soc in rk3399 rk3368 rk3328
do
mkdir -p %{buildroot}%{_datadir}/%{name}/$(echo $soc)/
 for file in bl31/bl31.elf m0/rk3399m0.bin m0/rk3399m0.elf
 do
  if [ -f build/$(echo $soc)/release/$(echo $file) ]; then
    install -p -m 0644 build/$(echo $soc)/release/$(echo $file) /%{buildroot}%{_datadir}/%{name}/$(echo $soc)/
  fi
 done
done

%files -n arm-trusted-firmware-armv8
%license license.rst
%doc readme.rst
%{_datadir}/%{name}
