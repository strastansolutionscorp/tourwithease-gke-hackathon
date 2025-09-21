import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const { audioContent, languageCode = "en-US" } = await request.json();

    if (!audioContent) {
      return NextResponse.json(
        { error: "Audio content is required" },
        { status: 400 }
      );
    }

    const response = await fetch(
      `https://speech.googleapis.com/v1/speech:recognize?key=${process.env.GOOGLE_API_KEY}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          config: {
            encoding: "WEBM_OPUS",
            sampleRateHertz: 48000,
            languageCode,
            enableAutomaticPunctuation: true,
            model: "latest_long",
          },
          audio: {
            content: audioContent,
          },
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Google Speech API error: ${response.status}`);
    }

    const data = await response.json();
    const transcript = data.results?.[0]?.alternatives?.[0]?.transcript || "";

    return NextResponse.json({
      transcript,
      confidence: data.results?.[0]?.alternatives?.[0]?.confidence || 0,
    });
  } catch (error) {
    console.error("Speech-to-Text error:", error);
    return NextResponse.json(
      { error: "Failed to recognize speech" },
      { status: 500 }
    );
  }
}
