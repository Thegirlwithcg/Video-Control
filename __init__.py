
bl_info = {
    "name": "Video Control",
    "description": "Add-on to control video speed and timeline settings in Blender VSE",
    "author": "Nichada Patthanawong",
    "version": (0, 1, 1),  # Tuple with three integers
    "blender": (4, 2, 0),  # Compatible with Blender 4.2.0 or later
    "category": "Video Editing",
    "license": "GPL"
}

# License: GPL-3.0-or-later with Attribution Requirement
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# Attribution Requirement:
# If you redistribute or modify this program, you must give credit to the
# original author: Nichada Patthanawong.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import bpy

# Operator: Adjust Speed for Video Only
class AdjustVideoSpeedOperator(bpy.types.Operator):
    bl_idname = "vse.adjust_video_speed"
    bl_label = "Adjust Video Speed"
    bl_description = "Adjust the speed of video sequences"

    def execute(self, context):
        # Get Speed Factor from Scene Property
        speed = context.scene.video_speed_factor

        # Get the selected sequences
        selected_sequences = [
            seq for seq in context.scene.sequence_editor.sequences if seq.select
        ]

        if not selected_sequences:
            self.report({'WARNING'}, "No video sequence selected!")
            return {'CANCELLED'}

        for seq in selected_sequences:
            if seq.type == 'MOVIE':  # Handle only MOVIE sequences
                # Check if Speed Control Effect exists
                speed_effect = None
                for effect in context.scene.sequence_editor.sequences_all:
                    if effect.type == 'SPEED' and effect.input_1 == seq:
                        speed_effect = effect
                        break

                if speed_effect:
                    # Update the speed factor in the existing Speed Control Effect
                    speed_effect.speed_factor = speed
                else:
                    # Add Speed Control Effect if not already exists
                    speed_effect = context.scene.sequence_editor.sequences.new_effect(
                        name=f"SpeedEffect_{seq.name}",
                        type='SPEED',
                        channel=seq.channel + 1,
                        frame_start=int(seq.frame_start),  # Ensure int type
                        frame_end=int(seq.frame_final_end),  # Ensure int type
                        seq1=seq
                    )
                    speed_effect.speed_factor = speed

                # Adjust timeline length based on speed
                original_length = seq.frame_duration
                new_length = abs(int(original_length / speed))  # Use absolute for negative speed
                seq.frame_final_end = seq.frame_final_start + new_length
            else:
                self.report({'WARNING'}, f"Sequence {seq.name} is not a video clip")

        # Refresh Sequencer to apply changes
        bpy.ops.sequencer.refresh_all()

        self.report({'INFO'}, f"Speed adjusted to {speed}x for selected video sequences")
        return {'FINISHED'}


# Operator: Set Final Frame
class SetEndFrameOperator(bpy.types.Operator):
    bl_idname = "vse.set_end_frame"
    bl_label = "Set End Frame"
    bl_description = "Set the final frame of the timeline to the length of the longest sequence"

    def execute(self, context):
        # Get all sequences and calculate the max frame length
        max_frame_length = max(
            (seq.frame_final_end for seq in context.scene.sequence_editor.sequences),
            default=0
        )

        if max_frame_length > 0:
            context.scene.frame_end = max_frame_length
            self.report({'INFO'}, f"Final frame set to {max_frame_length}")
        else:
            self.report({'WARNING'}, "No sequences found!")

        return {'FINISHED'}


# Panel: Video Control UI
class VideoControlPanel(bpy.types.Panel):
    bl_label = "Video Control"
    bl_idname = "VSE_PT_video_control"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Video Control"

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        # Add Speed Adjustment Section
        col.label(text="Adjust Video Speed")
        col.prop(context.scene, "video_speed_factor", text="Speed Factor")  # User Input
        col.operator("vse.adjust_video_speed", text="Set Speed Factor")

        # Add Set End Frame Section
        col.separator()
        col.label(text="Set Final Frame")
        col.operator("vse.set_end_frame", text="Set End Frame")


# Property: Global Speed Factor for UI
def init_properties():
    bpy.types.Scene.video_speed_factor = bpy.props.FloatProperty(
        name="Speed Factor",
        description="Global speed factor for selected video sequences",
        default=1.0,
        min=0.1,
        max=10.0,
    )


def clear_properties():
    del bpy.types.Scene.video_speed_factor


# Register Classes
classes = [
    AdjustVideoSpeedOperator,
    SetEndFrameOperator,
    VideoControlPanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    init_properties()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    clear_properties()


if __name__ == "__main__":
    register()
