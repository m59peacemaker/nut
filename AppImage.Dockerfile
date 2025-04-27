FROM ghcr.io/pkgforge-dev/archlinux:latest

ARG VERSION="dev"

RUN mkdir "/tmp/work" "/out"

WORKDIR "/tmp/work"

COPY ./scripts/install-arch-packages /tmp/work/

RUN /tmp/work/install-arch-packages

ENV QT_VERSION=6.8.1
ENV QT_VERSION_MAJOR=6

RUN pipx install aqtinstall

RUN "${HOME}/.local/bin/aqt" install-qt \
	--outputdir /opt/Qt \
	linux desktop \
	"${QT_VERSION}" \
	--modules qtimageformats qtwaylandcompositor

RUN mkdir "/usr/lib/qt${QT_VERSION_MAJOR}" \
	&& cp -a /opt/Qt/${QT_VERSION}/gcc_64/plugins "/usr/lib/qt${QT_VERSION_MAJOR}/" \
	&& cp -a /opt/Qt/${QT_VERSION}/gcc_64/qml "/usr/lib/qt${QT_VERSION_MAJOR}/" \
	&& cp -a /opt/Qt/${QT_VERSION}/gcc_64/lib/*.so /usr/lib/ \
	&& cp -a /opt/Qt/${QT_VERSION}/gcc_64/lib/*.so.* /usr/lib/ \
	&& rm -r /opt/Qt

RUN : \
	&& wget \
		"https://github.com/VHSgunzo/sharun/releases/latest/download/sharun-$(uname -m)-aio" \
		-O "/usr/local/bin/sharun" \
	&& chmod +x "/usr/local/bin/sharun"

RUN : \
	&& wget \
		"https://github.com/VHSgunzo/uruntime/releases/latest/download/uruntime-appimage-dwarfs-$(uname -m)" \
		-O "/usr/local/bin/uruntime" \
	&& chmod +x "/usr/local/bin/uruntime"

ENV NUT_DIR="usr/local/share/nut"

COPY ./requirements.txt "/${NUT_DIR}/requirements.txt"

RUN sharun lib4bin --strip --with-hooks --python-ver 3.13 --python-pkg "/${NUT_DIR}/requirements.txt" --dst-dir "/AppDir"

COPY . "/${NUT_DIR}"

RUN cp -a --parents "/${NUT_DIR}" "/AppDir"

RUN /AppDir/sharun python3 -m compileall "/AppDir/${NUT_DIR}"

RUN cp -a "/AppDir" "/AppDir_cli"

RUN sharun lib4bin --strace-mode --strace-time 5 --strip --with-hooks \
	--dst-dir "/AppDir_cli" \
	"/AppDir_cli/sharun" -- python3 "/AppDir_cli/${NUT_DIR}/nut.py"

RUN sharun lib4bin --dst-dir "/AppDir" --strip --with-hooks \
	/usr/lib/gtk-3.0/modules/* \
	/usr/lib/gio/modules/libgvfsdbus.so

RUN xvfb-run -a -- sharun lib4bin --strace-mode --strace-time 10 --strip --with-hooks \
	--dst-dir "/AppDir" \
	"/AppDir/sharun" -- python3 "/AppDir/${NUT_DIR}/nut_gui.py"

COPY ./scripts/AppRun_cli /AppDir_cli/AppRun
COPY ./scripts/AppRun /AppDir/AppRun
COPY ./nut.desktop /AppDir/
COPY ./images/logo@128x128.png /AppDir/nut.png

RUN uruntime --appimage-mkdwarfs -f \
	--set-owner 0 --set-group 0 \
	--no-history --no-create-timestamp \
	--compression zstd:level=22 -S26 -B32 \
	--header "$(which uruntime)" \
	-i /AppDir_cli -o "/out/nut-cli-v${VERSION}.AppImage"

RUN chmod +x "/out/nut-cli-v${VERSION}.AppImage"

RUN uruntime --appimage-mkdwarfs -f \
	--set-owner 0 --set-group 0 \
	--no-history --no-create-timestamp \
	--compression zstd:level=22 -S26 -B32 \
	--header "$(which uruntime)" \
	-i /AppDir -o "/out/nut-v${VERSION}.AppImage"

RUN chmod +x "/out/nut-v${VERSION}.AppImage"
