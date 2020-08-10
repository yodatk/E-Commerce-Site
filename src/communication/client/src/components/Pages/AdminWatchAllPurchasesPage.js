import React, {Component} from "react";
import axios from "axios";
import PurchaseTable from "../PurchaseTable";
import OnlyHeaderComponent from "../OnlyHeaderComponent";

export class AdminWatchAllPurchasesPage extends Component {
    state = {
        purchases: []
    }

    componentDidMount() {
        axios.get(
            "/fetch_all_purchases_as_admin/" + this.props.getUserId())
            .then((res) => {
                this.setState({purchases: res.data !== null && 'purchases' in res.data ? res.data.purchases : []})
                console.log(res.data.purchases)
            }).catch(error => {
            console.log(error)
        });
    }

    render() {
        if (this.props.isAdmin.bind(this)() && this.props.isLoggedIn.bind(this)()) {
            return (
                <PurchaseTable purchases={this.state.purchases}/>
            );
        } else {
            return <OnlyHeaderComponent header={"Only Admins Are Allowed here"}/>
        }

    }
}

export default AdminWatchAllPurchasesPage;