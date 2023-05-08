import os

# from random import randint
# from hypothesis import given, settings, strategies as st
import requests

from proxy.fault_decorators import fault_injection

# from requests import Response

TESTING_TIMEOUT: float = float(os.getenv("TESTING_TIMEOUT", "100"))

testing_data: dict[str, float] = {}


# def test_one_client_lock(
#     setup_token_ring_four_client,  # pylint: disable=unused-argument # pyright: ignore
# ):

#     client_lock_10_times()
# testing_data["none"] = avg_duration
# print(f"average time taken to lock the resource is {avg_duration} second")


# @fault_injection(["delay_all_small"])
# @fault_injection(["delay_all_medium"])
@fault_injection(["delay_all_large"])
def test_one_client_lock_with_small_delay(
    # setup_token_ring_four_client,  # pylint: disable=unused-argument # pyright: ignore
    load_faults_into_proxy,  # pylint: disable=unused-argument # pyright: ignore
):
    """
    This client is being injected with a 0.02 delay for all http requests
    """

    client_lock_10_times()


# assert avg_duration > 0
# print(f"average time taken to lock the resource is {avg_duration} second")
# testing_data["small"] = avg_duration


# @fault_injection(["delay_all_medium"])
# def test_one_client_lock_with_medium_delay(
#     # setup_token_ring_four_client,  # pylint: disable=unused-argument # pyright: ignore
#     load_faults_into_proxy,  # pylint: disable=unused-argument # pyright: ignore
# ):
#     """
#     This client is being injected with a 0.2 delay for all http requests
#     """
#     avg_duration = client_lock_10_times()
#     print(f"average time taken to lock the resource is {avg_duration} second")
#     testing_data["medium"] = avg_duration


# @fault_injection(["delay_all_large"])
# def test_one_client_lock_with_large_delay(
#     # setup_token_ring_four_client,  # pylint: disable=unused-argument # pyright: ignore
#     load_faults_into_proxy,  # pylint: disable=unused-argument # pyright: ignore
# ):
#     """
#     This client is being injected with a 0.5 delay for all http requests
#     """
#     avg_duration = client_lock_10_times()
#     print(f"average time taken to lock the resource is {avg_duration} second")
#     testing_data["large"] = avg_duration


# # def test_draw_plot():
# #     # Extract the labels (x-axis) and values (y-axis) from the testing_data dictionary
# #     labels = list(testing_data.keys())
# #     values = list(testing_data.values())

# #     # Create a bar chart using the labels and values
# #     plt.bar(labels, values)
# #     plt.xlabel("Delay Type")
# #     plt.ylabel("Duration (seconds)")
# #     plt.title("Average Time Taken to Lock the Resource")

# #     # Customize the y-axis to show the unit (seconds)
# #     plt.gca().yaxis.set_major_formatter(
# #         plt.FuncFormatter(lambda x, _: f"{x:.1f} s")
# #     )

# #     # Display the plot
# #     plt.show()


def client_lock_10_times() -> None:
    # total_duration: float = 0

    for _ in range(10):

        # start_time = time.time()

        requests.post(
            "http://127.0.0.1:5002/A/request",
            timeout=TESTING_TIMEOUT,
        )

        requests.put(
            "http://127.0.0.1:5003/A/token",
            timeout=TESTING_TIMEOUT,
        )

        requests.delete(
            "http://127.0.0.1:5002/A/lock",
            timeout=TESTING_TIMEOUT,
        )

        # assert r.status_code == 200
        # end_time = time.time()

        # load the end_time from enviroment variables END_TIME

        # possible_end: str = os.environ.get("END_TIME", "")
        # while len(possible_end) == 0:
        #     possible_end = os.environ.get("END_TIME", "")
        # os.environ["END_TIME"] = ""
        # end_time = float(possible_end)

    #     duration = end_time - start_time

    #     total_duration += duration

    # avg_duration = total_duration / 10

    # return avg_duration
