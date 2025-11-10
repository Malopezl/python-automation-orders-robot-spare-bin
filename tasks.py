from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=500)
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        fill_the_form(row)
    archive_receipts()

def open_robot_order_website():
    """Navigates to the RobotSpareBin Industries Inc. website."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def give_conscent():
    """Gives consent to cookies."""
    page = browser.page()
    page.click("button:text('OK')")

def get_orders():
    """Downloads the CSV file containing robot orders."""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

    tables = Tables()
    return tables.read_table_from_csv("orders.csv", header=True)

def fill_the_form(order):
    """Fills and submits the robot order form."""
    page = browser.page()
    give_conscent()
    page.select_option("#head", order["Head"])
    page.click(f"#id-body-{order['Body']}")
    page.fill("input[placeholder]", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#order")

    while page.is_visible("div[class='alert alert-danger']", timeout=3000):
        page.click("#order")

    store_receipt_as_pdf(order["Order number"])
    screenshot_robot()
    embed_screenshot_to_receipt(screenshot="output/robot.png", pdf_file=f"output/receipt_{order["Order number"]}.pdf")
    page.click("#order-another")

def store_receipt_as_pdf(order_number):
    """Exports the order receipt and robot image as a PDF file."""
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt, f"output/receipt_{order_number}.pdf")

def screenshot_robot():
    """Takes a screenshot of the robot image."""
    page = browser.page()
    return page.locator("#robot-preview-image").screenshot(path="output/robot.png")

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Appends the robot image screenshot to the PDF receipt."""
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    """Creates a ZIP archive of the receipts and robot images."""
    archive = Archive()
    archive.archive_folder_with_zip(folder="output", archive_name="robot_orders.zip", include="*.pdf")