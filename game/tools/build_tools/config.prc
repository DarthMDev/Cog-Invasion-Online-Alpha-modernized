# BEGIN PANDA3D CONFIG
load-file-type egg pandaegg
load-audio-type * p3ffmpeg
load-video-type * p3ffmpeg
egg-object-type-portal          <Scalar> portal { 1 }
egg-object-type-polylight       <Scalar> polylight { 1 }
egg-object-type-seq24           <Switch> { 1 } <Scalar> fps { 24 }
egg-object-type-seq12           <Switch> { 1 } <Scalar> fps { 12 }
egg-object-type-indexed         <Scalar> indexed { 1 }
egg-object-type-seq10           <Switch> { 1 } <Scalar> fps { 10 }
egg-object-type-seq8            <Switch> { 1 } <Scalar> fps { 8 }
egg-object-type-seq6            <Switch> { 1 } <Scalar>  fps { 6 }
egg-object-type-seq4            <Switch> { 1 } <Scalar>  fps { 4 }
egg-object-type-seq2            <Switch> { 1 } <Scalar>  fps { 2 }
egg-object-type-binary          <Scalar> alpha { binary }
egg-object-type-dual            <Scalar> alpha { dual }
egg-object-type-glass           <Scalar> alpha { blend_no_occlude }
egg-object-type-model           <Model> { 1 }
egg-object-type-dcs             <DCS> { 1 }
egg-object-type-notouch         <DCS> { no_touch }
egg-object-type-barrier         <Collide> { Polyset descend }
egg-object-type-sphere          <Collide> { Sphere descend }
egg-object-type-invsphere       <Collide> { InvSphere descend }
egg-object-type-tube            <Collide> { Tube descend }
egg-object-type-trigger         <Collide> { Polyset descend intangible }
egg-object-type-trigger-sphere  <Collide> { Sphere descend intangible }
egg-object-type-floor           <Collide> { Polyset descend level }
egg-object-type-dupefloor       <Collide> { Polyset keep descend level }
egg-object-type-bubble          <Collide> { Sphere keep descend }
egg-object-type-ghost           <Scalar> collide-mask { 0 }
egg-object-type-glow            <Scalar> blend { add }
egg-object-type-direct-widget   <Scalar> collide-mask { 0x80000000 } <Collide> { Polyset descend }
cull-bin gui-popup 60 unsorted
default-model-extension .egg
load-display pandagl
aux-display p3tinydisplay
win-origin -2 -2
win-size 800 600
fullscreen #f
framebuffer-hardware #t
framebuffer-software #f
depth-bits 1
color-bits 1
alpha-bits 0
stencil-bits 0
multisamples 0
notify-level warning
default-directnotify-level warning
want-directtools  #f
want-tk           #f
want-pstats            #f
show-frame-rate-meter  #f
use-movietexture #t
hardware-animated-vertices #f
model-cache-dir $USER_APPDATA/Panda3D-1.10/cache
model-cache-textures #f
basic-shaders-only #f
# END PANDA3D CONFIG

# Now, config for cog invasion online

# Default window properties...
window-title Cog Invasion Online (Alpha)
win-origin -1 -1
win-size 640 480
load-display pandagl

# Logging...
notify-level warning
default-directnotify-level warning

# Filenames...
cursor-filename toonmono.cur
icon-filename icon.ico

default-model-extension .egg

model-cache-model #t
model-cache-textures #t

model-path .

# Audio...

# Woo-hoo!!!! Miles!!
audio-library-name null

# Virtual file system...
vfs-mount phase_3.mf /
vfs-mount phase_3.5.mf /
vfs-mount phase_4.mf /
vfs-mount phase_5.mf /
vfs-mount phase_5.5.mf /
vfs-mount phase_6.mf /
vfs-mount phase_7.mf /
vfs-mount phase_8.mf /
vfs-mount phase_9.mf /
vfs-mount phase_10.mf /
vfs-mount phase_11.mf /
vfs-mount phase_12.mf /
vfs-mount phase_13.mf /

# Performance...
hardware-animated-vertices #f
sync-video #f
smooth-lag 0.2
basic-shaders-only #f
framebuffer-multisample 1
multisamples 16

# Game content...
game-name Cog Invasion
want-weapons #t
want-pies #t
want-chat #t
want-sa-reactions #f

want-pstats 0

egg-load-old-curves 0
