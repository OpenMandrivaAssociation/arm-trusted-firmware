#global candidate rc1
# ./make-git-snapshot.sh
#global snapshot 20190209

# Binaries not used in standard manner so debuginfo is useless
%global debug_package %{nil}

Name:    arm-trusted-firmware
Version: 2.1
Release: 2%{?candidate:.%{candidate}}%{?snapshot:.%{snapshot}}%{?dist}
Summary: ARM Trusted Firmware
License: BSD
URL:     https://github.com/ARM-software/arm-trusted-firmware/wiki

%if 0%{?snapshot}
Source0:  arm-trusted-firmware-%{snapshot}.tar.xz
%else
Source0:  https://github.com/ARM-software/arm-trusted-firmware/archive/v%{version}%{?candidate:-%{candidate}}.tar.gz
%endif

# At the moment we're only building on aarch64
ExclusiveArch: aarch64

BuildRequires: dtc
BuildRequires: gcc

%description
ARM Trusted firmware is a reference implementation of secure world software for
ARMv8-A including Exception Level 3 (EL3) software. It provides a number of
standard ARM interfaces like Power State Coordination (PSCI), Trusted Board
Boot Requirements (TBBR) and Secure Monitor.

Note: the contents of this package are generally just consumed by bootloaders
such as u-boot. As such the binaries aren't of general interest to users.

%ifarch aarch64
%package     -n arm-trusted-firmware-armv8
Summary:     ARM Trusted Firmware for ARMv8-A

%description -n arm-trusted-firmware-armv8
ARM Trusted Firmware binaries for various  ARMv8-A SoCs.

Note: the contents of this package are generally just consumed by bootloaders
such as u-boot. As such the binaries aren't of general interest to users.
%endif

%prep
%if 0%{?snapshot}
%autosetup -n %{name}-%{snapshot}
%else
%autosetup -n %{name}-%{version}%{?candidate:-%{candidate}}
%endif

# Fix the name of the cross compile for the rk3399 Cortex-M0 PMU
sed -i 's/arm-none-eabi-//' plat/rockchip/rk3399/drivers/m0/Makefile

%build
%ifarch aarch64
for soc in hikey hikey960 imx8qm imx8qx juno a3700 gxbb rk3399 rk3368 rk3328 rpi3 sun50i_a64 sun50i_h6 zynqmp
do
# At the moment we're only making the secure firmware (bl31)
make HOSTCC="gcc $RPM_OPT_FLAGS" CROSS_COMPILE="" PLAT=$(echo $soc) bl31
done
%endif

%install
mkdir -p %{buildroot}%{_datadir}/%{name}

%ifarch aarch64
# Most platforms want bl31.bin
for soc in hikey hikey960 imx8qm imx8qx juno rpi3 sun50i_a64 sun50i_h6 zynqmp
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

%endif

%ifarch aarch64
%files -n arm-trusted-firmware-armv8
%license license.rst
%doc readme.rst
%{_datadir}/%{name}
%endif
