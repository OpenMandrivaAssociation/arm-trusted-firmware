# Binaries not used in standard manner so debuginfo is useless
%global debug_package %{nil}

Name:		arm-trusted-firmware
Version:	2.12.0
Release:	1
Summary:	ARM Trusted Firmware
License:	BSD
Group:		Development/C
URL:		https://github.com/ARM-software/arm-trusted-firmware/wiki
Source0:	https://github.com/ARM-software/arm-trusted-firmware/archive/v%{version}.tar.gz

BuildRequires:	dtc
BuildRequires:	gcc

BuildArch:	noarch

%ifnarch %{arm}
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-gcc-bootstrap
BuildRequires:	cross-armv7hnl-openmandriva-linux-gnueabihf-binutils
%endif
%ifnarch %{aarch64}
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-gcc-bootstrap
BuildRequires:	cross-aarch64-openmandriva-linux-gnu-binutils
%endif

%patchlist
https://src.fedoraproject.org/rpms/arm-trusted-firmware/raw/rawhide/f/rk356x-scmi-clk-reset.patch
atf-2.12-sun50i-asm-clang.patch
atf-2.12-qti-clang.patch
atf-2.12-mediatek-clang.patch
atf-2.12-marvell-clang.patch
atf-2.12-agilex-clang.patch
atf-2.12-no-Lusrlib.patch

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

# Fix the name of the cross compile for 32-bit targets
sed -i 's/arm-none-eabi-/armv7hnl-linux-gnueabihf-/' make_helpers/toolchains/aarch32.mk make_helpers/toolchains/rk3399-m0.mk plat/rockchip/rk3399/drivers/m0/Makefile

%build
%undefine _auto_set_build_flags

BOARDS=$(make PLAT=this_does_not_exist 2>&1 |grep available |sed -e 's,.*available: ,,;s,\".*,,;s,|, ,g')
for soc in $BOARDS; do
	case $soc in
	a5ds|corstone700|fvp_ve|rk3288)
		# aarch32 platform without bl31, needs AARCH32_SP
		;;
	a70x0|a70x0_amc|a70x0_mochabin|a80x0|a80x0_mcbin|a80x0_puzzle|t9130|t9130_cex7_eval)
		# Needs SCP_BL2
		;;
	mdm9607|msm8909|picopi|warp7)
		# 32-bit target, need to specify ARCH=aarch32 
		;;
	mt8186|mt8192|mt8195)
		# Seems broken: UART_CLOCK undefined
		;;
	mt8188)
		# Seems broken: error: use of undeclared identifier 'BOOT_ARG_FROM_BL2'
		;;
	imx8mq)
		# Seems broken (undefined imx_hab_handler), and probably is a dupe of imx8qm
		;;
	morello)
		# Seems broken (bad platform.mk)
		;;
	npcm845x)
		# Need to set BL32_BASE -- probably board specific
		;;
	rcar|rzg)
		# Need to specify LSI -- probably board specific
		;;
	rdv3)
		# Needs mbedtls for bare metal
		;;
	sc7180|sc7280)
		# undefined symbol: coreboot_get_memory_type
		;;
	tc)
		# "Platform tc is no longer available"
		;;
	tegra)
		for s in plat/nvidia/tegra/soc/*; do
			tsoc=$(basename $s)
			make HOSTCC="cc $RPM_OPT_FLAGS" CC="cc" aarch64-cc-id=llvm-clang aarch64-ld-id=llvm-lld aarch32-cc-id=llvm-clang aarch32-ld-id=llvm-lld CROSS_COMPILE="aarch64-openmandriva-linux-gnu-" CROSS_COMPILE32="armv7hnl-linux-gnueabihf-" PLAT=$soc TARGET_SOC=$tsoc ERRORS=-Wno-error bl31
		done
		;;
	corstone*)
		make HOSTCC="cc $RPM_OPT_FLAGS" CC="cc" aarch64-cc-id=llvm-clang aarch64-ld-id=llvm-lld aarch32-cc-id=llvm-clang aarch32-ld-id=llvm-lld CROSS_COMPILE="aarch64-openmandriva-linux-gnu-" CROSS_COMPILE32="armv7hnl-linux-gnueabihf-" PLAT=$soc TARGET_PLATFORM=fvp bl31
		;;
	k3)
		for s in plat/ti/k3/board/*; do
			make HOSTCC="cc $RPM_OPT_FLAGS" CROSS_COMPILE="aarch64-openmandriva-linux-gnu-" CROSS_COMPILE32="armv7hnl-linux-gnueabihf-" PLAT=$soc TARGET_BOARD=$(basename $s) SPD=opteed K3_USART=0x8 bl31
		done
		;;
	qemu_sbsa)
		make HOSTCC="cc $RPM_OPT_FLAGS" CC="cc" aarch64-cc-id=llvm-clang aarch64-ld-id=llvm-lld aarch32-cc-id=llvm-clang aarch32-ld-id=llvm-lld CROSS_COMPILE="aarch64-openmandriva-linux-gnu-" CROSS_COMPILE32="armv7hnl-linux-gnueabihf-" PLAT=$soc all fip
		;;
	imx*|stm32mp2|uniphier|rk3399|rk3588|poplar|rdn1edge|rdn2|rdv1|rdv1mc|sgi575|fvp_r)
		# Generally the same as "normal", but needs to be built with gcc
		# Mostly asm code that needs adjustments and -fPIC/-pie conflicts
		make HOSTCC="cc $RPM_OPT_FLAGS" CROSS_COMPILE="aarch64-openmandriva-linux-gnu-" CROSS_COMPILE32="armv7hnl-linux-gnueabihf-" PLAT=$soc bl31
		;;
	*)
		make HOSTCC="cc $RPM_OPT_FLAGS" CC="cc" aarch64-cc-id=llvm-clang aarch64-ld-id=llvm-lld aarch32-cc-id=llvm-clang aarch32-ld-id=llvm-lld CROSS_COMPILE="aarch64-openmandriva-linux-gnu-" CROSS_COMPILE32="armv7hnl-linux-gnueabihf-" PLAT=$soc ERRORS=-Wno-error bl31
		;;
	esac
done

%install
cd build
find . -type d -name release |while read r; do
	board=$(dirname $r |sed -e 's,^./,,;s,/,-,g')
	mkdir -p %{buildroot}%{_datadir}/%{name}/$board/
	find $r -name "*.elf" -o -name "*.bin" |while read f; do
		install -pD -m 0644 $f %{buildroot}%{_datadir}/%{name}/$board/
	done
	if rmdir %{buildroot}%{_datadir}/%{name}/$board; then
		echo "Board contains no *.bin/*.elf files: $board"
		exit 1
	fi
done

%files -n arm-trusted-firmware-armv8
%license license.rst
%doc readme.rst
%{_datadir}/%{name}
