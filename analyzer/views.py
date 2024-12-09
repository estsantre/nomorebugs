from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from error_tracker.models import ErrorLog
from django.shortcuts import get_object_or_404


class AnalyzeBugView(APIView):
    def get(self, request, errorLogId):
        """
        Analyzes an error log based on the provided errorLogId.
        """
        # Retrieve the ErrorLog object
        error_log = get_object_or_404(ErrorLog, id=errorLogId)

        # Prepare the OpenAI API prompt
        prompt = (
            f"Analyze the following error log:\n\n"
            f"Error Message: {error_log.error_message}\n"
            f"Environment: {error_log.environment or 'N/A'}\n"
            f"Timestamp: {error_log.created_at}\n\n"
            "What could be the possible cause of this error, and what steps can fix it?"
        )

        return Response({'analysis': prompt}, status=status.HTTP_200_OK)

        # try:
        #     # Call the OpenAI API
        #     openai.api_key = "your-openai-api-key"
        #     response = openai.ChatCompletion.create(
        #         model="gpt-4",
        #         messages=[
        #             {"role": "system", "content": "You are a software debugging assistant."},
        #             {"role": "user", "content": prompt},
        #         ],
        #     )
        #
        #     analysis = response.choices[0].message['content']
        #
        #     # Return the analysis result
        #     return Response({'analysis': analysis}, status=status.HTTP_200_OK)
        #
        # except OpenAIError as e:
        #     # Handle OpenAI API errors
        #     return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
