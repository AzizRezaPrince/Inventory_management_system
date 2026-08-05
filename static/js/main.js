document.addEventListener('DOMContentLoaded', () => {
    console.log("Electronics Shop Inventory & Repair Management System Loaded.");

    // Flash Alert Dismissal
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Modal Helper Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Table Search Filter
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        let cells = rows[i].getElementsByTagName('td');
        let match = false;
        for (let j = 0; j < cells.length; j++) {
            if (cells[j] && cells[j].textContent.toLowerCase().indexOf(filter) > -1) {
                match = true;
                break;
            }
        }
        rows[i].style.display = match ? '' : 'none';
    }
}

// Repair Receipt Modal Printer with Dynamic Shop Settings (Bangladeshi Taka)
function printRepairReceipt(id, customer, phone, device, problem, cost, advance, status, delivery, date) {
    const balance = (parseFloat(cost) - parseFloat(advance)).toFixed(2);
    const shop = window.SHOP_SETTINGS || {
        name: 'ElectroIMS',
        tagline: 'Electronics Shop & Repair Hub',
        phone: '01700000000',
        address: 'Dhaka, Bangladesh'
    };

    const receiptHTML = `
        <div id="printableReceipt" style="font-family: Arial, sans-serif; color: #111; padding: 20px; border: 2px solid #333; max-width: 520px; margin: auto; background: #fff;">
            <div style="text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 15px;">
                <h2 style="margin: 0; text-transform: uppercase; letter-spacing: 1px;">${shop.name}</h2>
                <p style="margin: 4px 0; font-size: 0.9rem; color: #444;">${shop.tagline}</p>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">Phone: ${shop.phone} | ${shop.address}</p>
                <h4 style="margin-top: 10px; margin-bottom: 0; background: #222; color: #fff; padding: 4px; font-size: 0.9rem;">REPAIR SERVICE RECEIPT</h4>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 0.9rem; font-weight: bold;">
                <span>Ticket #: ${id}</span>
                <span>Date: ${date}</span>
            </div>
            
            <hr style="border: 0.5px solid #ccc; margin-bottom: 12px;">
            
            <p style="margin: 4px 0;"><strong>Customer Name:</strong> ${customer}</p>
            <p style="margin: 4px 0;"><strong>Contact Phone:</strong> ${phone || 'N/A'}</p>
            <p style="margin: 4px 0;"><strong>Device Item:</strong> ${device}</p>
            <p style="margin: 4px 0;"><strong>Reported Issue:</strong> ${problem}</p>
            <p style="margin: 4px 0;"><strong>Est. Delivery Date:</strong> ${delivery || 'TBD'}</p>
            <p style="margin: 4px 0;"><strong>Status:</strong> <span style="text-transform: uppercase; font-weight: bold;">${status}</span></p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr style="background: #f0f0f0;">
                    <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Item / Description</th>
                    <th style="padding: 8px; border: 1px solid #ddd; text-align: right;">Amount (Tk)</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">Repair Labor & Replacement Parts Charge</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">Tk ${parseFloat(cost).toFixed(2)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Advance Paid Deposit</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right; color: green; font-weight: bold;">-Tk ${parseFloat(advance).toFixed(2)}</td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; font-size: 1rem;">Balance Due at Delivery</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold; font-size: 1rem; color: red;">Tk ${balance}</td>
                </tr>
            </table>

            <div style="margin-top: 35px; display: flex; justify-content: space-between; text-align: center; font-size: 0.85rem;">
                <div>
                    <br><br>
                    ______________________<br>
                    Customer Signature
                </div>
                <div>
                    <br><br>
                    ______________________<br>
                    Authorized Technician
                </div>
            </div>
            
            <p style="text-align: center; font-size: 0.75rem; color: #777; margin-top: 25px;">Thank you for choosing ${shop.name}! Please bring this receipt for pickup.</p>
        </div>
    `;

    let receiptContainer = document.getElementById('receiptModalBody');
    if (receiptContainer) {
        receiptContainer.innerHTML = receiptHTML;
        openModal('receiptModal');
    }
}

// Product Sales Cash Memo Invoice Printer (Bangladeshi Taka)
function printSalesReceipt(saleId, date, pcode, pname, cname, ccode, qty, unitPrice, revenue, soldBy) {
    const shop = window.SHOP_SETTINGS || {
        name: 'ElectroIMS',
        tagline: 'Electronics Shop & Repair Hub',
        phone: '01700000000',
        address: 'Dhaka, Bangladesh'
    };

    const receiptHTML = `
        <div id="printableReceipt" style="font-family: Arial, sans-serif; color: #111; padding: 20px; border: 2px solid #333; max-width: 520px; margin: auto; background: #fff;">
            <div style="text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 15px;">
                <h2 style="margin: 0; text-transform: uppercase; letter-spacing: 1px;">${shop.name}</h2>
                <p style="margin: 4px 0; font-size: 0.9rem; color: #444;">${shop.tagline}</p>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">Phone: ${shop.phone} | ${shop.address}</p>
                <h4 style="margin-top: 10px; margin-bottom: 0; background: #10b981; color: #fff; padding: 4px; font-size: 0.9rem;">OFFICIAL SALES CASH MEMO</h4>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 0.9rem;">
                <span><strong>Invoice #:</strong> INV-${saleId}</span>
                <span><strong>Date:</strong> ${date}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 0.9rem;">
                <span><strong>Customer:</strong> ${cname} (${ccode})</span>
                <span><strong>Billed By:</strong> ${soldBy}</span>
            </div>
            
            <hr style="border: 0.5px solid #ccc; margin-bottom: 12px;">
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background: #f0f0f0;">
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Product Item</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: center;">Qty</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: right;">Unit Price</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: right;">Total (Tk)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">${pname} <br><small style="color:#666;">Code: ${pcode}</small></td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">${qty}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">Tk ${parseFloat(unitPrice).toFixed(2)}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: right; font-weight: bold;">Tk ${parseFloat(revenue).toFixed(2)}</td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td colspan="3" style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold; font-size: 1rem;">Total Net Amount Paid:</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: right; font-weight: bold; font-size: 1.1rem; color: #10b981;">Tk ${parseFloat(revenue).toFixed(2)}</td>
                    </tr>
                </tbody>
            </table>

            <div style="margin-top: 35px; display: flex; justify-content: space-between; text-align: center; font-size: 0.85rem;">
                <div>
                    <br><br>
                    ______________________<br>
                    Customer Signature
                </div>
                <div>
                    <br><br>
                    ______________________<br>
                    Authorized Seller
                </div>
            </div>
            
            <p style="text-align: center; font-size: 0.75rem; color: #777; margin-top: 25px;">Thank you for shopping at ${shop.name}! Please keep this receipt for warranty claims.</p>
        </div>
    `;

    let salesReceiptContainer = document.getElementById('salesReceiptModalBody');
    if (salesReceiptContainer) {
        salesReceiptContainer.innerHTML = receiptHTML;
        openModal('salesReceiptModal');
    }
}
