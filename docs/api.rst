Clip Objects
------------

External API (for GUI):

.. code-block:: python

    clip = Clip('test.wav', start=0.22, y=0.5, muted=False)

    clip.filename   # Name of WAV file.
    clip.start      # Start position in seconds (passed in, read only)
    clip.length     # Length in seconds (computed from file, read only)
    clip.muted      # True / False. Settable and gettable.
    clip.recording  # True if the clip is being recorded.
                    # This can be used to highlight the clip in the GUI.
                    # clip.end will grow as new data is recorded.
                    # (Read only for GUI.)

Internal API (for transport / audio engine):

.. code-block:: python

    # For internal use:
    clip.start_block  # Start position in blocks.
                      # (Rounded down to nearest block)
    clip.num_blocks   # Number of blocks in clip.
                      # (End is rounded up to nearest block.)

    clip.get_block(pos)  # Get block at block position 'pos'.
                         # Returns None if the clip has no block there.


Summing Audio
^^^^^^^^^^^^^

.. code-block:: python

    import audio

    block = audio.sum_blocks(clip.get_block(pos) for clip in clips)

``sum_blocks()`` treats ``None`` values as silence.
